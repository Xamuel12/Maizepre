import os

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from .ml.config import INPUT_FEATURES
from .ml.infer import predict_yield
from .storage.user_store import UserStore


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    # Basic configuration
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    user_store = UserStore(os.path.join(
        os.path.dirname(__file__), "storage", "users.json"))

    @app.get("/")
    def home():
        return render_template("home.html")

    @app.get("/signup")
    def signup_get():
        return render_template("signup.html")

    @app.post("/signup")
    def signup_post():
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        if not email or not password:
            flash("Email and password are required.", "danger")
            return redirect(url_for("signup_get"))

        username = (request.form.get("username") or "").strip().lower()
        first_name = (request.form.get("first_name") or "").strip()
        last_name = (request.form.get("last_name") or "").strip()

        password_confirm = request.form.get("confirm_password") or ""
        if password_confirm != password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("signup_get"))

        # Optional fields
        age_raw = (request.form.get("age") or "").strip()
        occupation = (request.form.get("occupation") or "").strip()
        age = None
        if age_raw:
            try:
                age = int(age_raw)
            except ValueError:
                flash("Age must be a number.", "danger")
                return redirect(url_for("signup_get"))

        if not username:
            flash("Username is required.", "danger")
            return redirect(url_for("signup_get"))
        if not first_name or not last_name:
            # Allow accounts even if names are empty (prevents user lockout)
            first_name = first_name or ""
            last_name = last_name or ""

        if user_store.exists_by_email(email) or user_store.exists_by_username(username):
            flash("Account already exists. Please login.", "warning")
            return redirect(url_for("login_get"))

        # Debug logging (visible in server console when you POST /signup)
        print(
            "[SIGNUP] received:",
            {
                "email": email,
                "username": username,
                "password_len": len(password) if password is not None else None,
                "confirm_len": len(password_confirm) if password_confirm is not None else None,
                "passwords_match": password_confirm == password,
            },
            flush=True,
        )

        user_store.create_user(
            email=email,
            username=username,
            password_hash=generate_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            age=age,
            occupation=occupation,
        )

        flash("Signup successful. Please login.", "success")
        return redirect(url_for("login_get"))

    @app.get("/login")
    def login_get():
        return render_template("login.html")

    @app.post("/login")
    def login_post():
        username = (request.form.get("username") or "").strip().lower()
        password = request.form.get("password") or ""

        user = user_store.get_user_by_username(username)
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid username or password.", "danger")
            return redirect(url_for("login_get"))

        # keep session key name used by UI/auth
        session["user_email"] = user.get("email")
        session["username"] = user.get("username")
        flash("Logged in successfully.", "success")
        return redirect(url_for("predict_get"))

    @app.get("/logout")
    def logout():
        session.pop("user_email", None)
        flash("Logged out.", "info")
        return redirect(url_for("home"))

    def login_required(func):
        def wrapper(*args, **kwargs):
            if "user_email" not in session:
                flash("Please login to access prediction.", "warning")
                return redirect(url_for("login_get"))
            return func(*args, **kwargs)

        # Keep Flask happy
        wrapper.__name__ = func.__name__
        return wrapper

    @app.get("/predict")
    @login_required
    def predict_get():
        return render_template("predict.html", features=INPUT_FEATURES)

    @app.post("/predict")
    @login_required
    def predict_post():
        # Collect and validate numeric inputs
        payload = {}
        errors = []
        for feature in INPUT_FEATURES:
            raw = request.form.get(feature)
            try:
                payload[feature] = float(raw)
            except (TypeError, ValueError):
                errors.append(f"{feature} must be a number.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("predict.html", features=INPUT_FEATURES, payload=payload)

        try:
            pred = predict_yield(payload)
        except FileNotFoundError:
            flash(
                "Model artifacts not found. Train the model first (see backend/ml/README).", "danger"
            )
            return render_template("predict.html", features=INPUT_FEATURES, payload=payload)
        except Exception as e:
            flash(f"Prediction failed: {e}", "danger")
            return render_template("predict.html", features=INPUT_FEATURES, payload=payload)

        # Render prediction directly (no redirect), so user can predict again immediately.
        return render_template("predict.html", features=INPUT_FEATURES, prediction=pred, payload=payload)

    return app
