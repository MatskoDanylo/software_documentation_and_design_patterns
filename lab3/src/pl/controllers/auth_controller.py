from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for

from src.bll.auth_service import AuthService


def create_auth_blueprint(auth_service: AuthService) -> Blueprint:
    auth_bp = Blueprint("auth", __name__)

    @auth_bp.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            try:
                token = auth_service.login(username, password)
            except ValueError as exc:
                flash(str(exc), "danger")
                return render_template("login.html", username=username)

            response = redirect(url_for("employee.list_employees"))
            response.set_cookie(
                "auth_token",
                token,
                httponly=True,
                samesite="Lax",
                secure=False,
                max_age=3600,
            )
            flash("Login successful.", "success")
            return response

        return render_template("login.html", username="")

    @auth_bp.post("/logout")
    def logout():
        response = redirect(url_for("employee.list_employees"))
        response.delete_cookie("auth_token")
        flash("Logged out.", "success")
        return response

    return auth_bp
