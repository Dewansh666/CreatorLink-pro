import os
import sqlite3
from flask import Flask, render_template, request, redirect, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
import razorpay

# ---------------- APP CONFIG ----------------

app = Flask(__name__)
app.secret_key = "supersecretkey"  # change later

# ---------------- RAZORPAY CONFIG (TEST MODE) ----------------

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

razorpay_client = None
if RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
    razorpay_client = razorpay.Client(
        auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
    )

# ---------------- DATABASE HELPERS ----------------

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def get_user_by_username(username):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cur.fetchone()
    conn.close()
    return user

def get_links(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM links WHERE user_id = ?", (user_id,))
    links = cur.fetchall()
    conn.close()
    return links

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    if "user_id" in session:
        return redirect("/dashboard")
    return redirect("/signup")

# ---------------- SIGNUP ----------------

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        username = request.form["username"]
        password = request.form["password"]

        if get_user_by_username(username):
            return "Username already exists"

        hashed = generate_password_hash(password)

        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (username, name, bio, avatar, password, plan, theme)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (username, name, "New Creator 🚀", "avatar.png", hashed, "free", "blue"))
        conn.commit()
        conn.close()

        user = get_user_by_username(username)
        session["user_id"] = user["id"]
        session["username"] = user["username"]

        return redirect("/dashboard")

    return render_template("signup.html")

# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = get_user_by_username(username)
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect("/dashboard")

        return "Invalid credentials"

    return render_template("login.html")

# ---------------- DASHBOARD ----------------

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    user = get_user_by_username(session["username"])

    if request.method == "POST":
        title = request.form["title"]
        url = request.form["url"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO links (user_id, title, url) VALUES (?, ?, ?)",
            (user["id"], title, url)
        )
        conn.commit()
        conn.close()

        return redirect("/dashboard")

    links = get_links(user["id"])
    return render_template("dashboard.html", user=user, links=links)

# ---------------- UPGRADE (CREATE ORDER – TEST MODE) ----------------

@app.route("/upgrade")
def upgrade():
    if "user_id" not in session:
        return redirect("/login")

    if not razorpay_client:
        return "Razorpay keys not configured. Set env vars.", 500

    order = razorpay_client.order.create({
        "amount": 9900,  # ₹99 in paise
        "currency": "INR",
        "payment_capture": 1
    })

    return render_template(
        "upgrade.html",
        order=order,
        key_id=RAZORPAY_KEY_ID
    )

# ---------------- PAYMENT SUCCESS (VERIFY SIGNATURE) ----------------

@app.route("/payment-success", methods=["POST"])
def payment_success():
    if not razorpay_client:
        return "Razorpay not configured", 500

    params = {
        "razorpay_order_id": request.form.get("razorpay_order_id"),
        "razorpay_payment_id": request.form.get("razorpay_payment_id"),
        "razorpay_signature": request.form.get("razorpay_signature"),
    }

    try:
        razorpay_client.utility.verify_payment_signature(params)
    except:
        abort(400)

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET plan='pro' WHERE id=?",
        (session["user_id"],)
    )
    conn.commit()
    conn.close()

    return redirect("/dashboard")

# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------- PUBLIC PROFILE ----------------

@app.route("/<username>")
def profile(username):
    user = get_user_by_username(username)
    if not user:
        return "User not found", 404

    links = get_links(user["id"])
    return render_template("profile.html", user=user, links=links)

# ---------------- RUN SERVER (RENDER SAFE) ----------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 CreatorLink Pro running on port {port}")
    app.run(host="0.0.0.0", port=port)
