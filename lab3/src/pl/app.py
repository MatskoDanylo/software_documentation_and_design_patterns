from __future__ import annotations

from flask import Flask

from src.bll.employee_service import EmployeeService
from src.pl.controllers.employee_controller import create_employee_blueprint


def create_app(employee_service: EmployeeService) -> Flask:
    app = Flask(__name__, template_folder="templates")
    app.config["SECRET_KEY"] = "dev-secret-key"

    employee_blueprint = create_employee_blueprint(employee_service)
    app.register_blueprint(employee_blueprint)

    return app
