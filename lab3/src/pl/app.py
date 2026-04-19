from __future__ import annotations

from flask import Flask, request

from src.bll.auth_service import AuthService
from src.bll.employee_service import EmployeeService
from src.pl.controllers.auth_controller import create_auth_blueprint
from src.pl.controllers.employee_controller import create_employee_blueprint


def create_app(employee_service: EmployeeService, auth_service: AuthService) -> Flask:
    app = Flask(__name__, template_folder="templates")
    app.config["SECRET_KEY"] = "dev-secret-key"

    auth_blueprint = create_auth_blueprint(auth_service)
    app.register_blueprint(auth_blueprint)

    employee_blueprint = create_employee_blueprint(employee_service, auth_service)
    app.register_blueprint(employee_blueprint)

    @app.context_processor
    def inject_auth_state() -> dict[str, object]:
        token = request.cookies.get("auth_token")
        current_user = auth_service.verify_token(token)
        return {"current_user": current_user}

    return app
