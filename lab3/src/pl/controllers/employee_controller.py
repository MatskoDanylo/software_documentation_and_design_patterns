from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for

from src.bll.auth_service import AuthService
from src.bll.employee_service import EmployeeService
from src.pl.middleware import require_auth


def create_employee_blueprint(
    employee_service: EmployeeService, auth_service: AuthService
) -> Blueprint:
    employee_bp = Blueprint("employee", __name__)

    @employee_bp.get("/")
    def home_redirect():
        return redirect(url_for("employee.list_employees"))

    @employee_bp.get("/employees")
    def list_employees():
        employees = employee_service.get_all()
        return render_template("employee_list.html", employees=employees)

    @employee_bp.route("/employees/create", methods=["GET", "POST"])
    @require_auth(auth_service)
    def create_employee():
        if request.method == "POST":
            form_data = {
                "employee_id": request.form.get("employee_id", ""),
                "first_name": request.form.get("first_name", ""),
                "last_name": request.form.get("last_name", ""),
                "email": request.form.get("email", ""),
                "start_date": request.form.get("start_date", ""),
                "position": request.form.get("position", ""),
            }
            try:
                employee_service.create(form_data)
                flash("Employee created successfully.", "success")
                return redirect(url_for("employee.list_employees"))
            except Exception as exc:
                flash(str(exc), "danger")
                return render_template(
                    "employee_form.html",
                    employee=form_data,
                    is_edit=False,
                    submit_label="Create",
                )

        return render_template(
            "employee_form.html",
            employee={},
            is_edit=False,
            submit_label="Create",
        )

    @employee_bp.route("/employees/<string:emp_id>/edit", methods=["GET", "POST"])
    @require_auth(auth_service)
    def edit_employee(emp_id: str):
        employee = employee_service.get_by_id(emp_id)
        if employee is None:
            flash("Employee not found.", "warning")
            return redirect(url_for("employee.list_employees"))

        if request.method == "POST":
            form_data = {
                "first_name": request.form.get("first_name", ""),
                "last_name": request.form.get("last_name", ""),
                "email": request.form.get("email", ""),
                "start_date": request.form.get("start_date", ""),
                "position": request.form.get("position", ""),
            }
            try:
                employee_service.update(emp_id, form_data)
                flash("Employee updated successfully.", "success")
                return redirect(url_for("employee.list_employees"))
            except Exception as exc:
                flash(str(exc), "danger")
                merged_employee = {
                    "employee_id": emp_id,
                    **form_data,
                }
                return render_template(
                    "employee_form.html",
                    employee=merged_employee,
                    is_edit=True,
                    submit_label="Save changes",
                )

        return render_template(
            "employee_form.html",
            employee=employee,
            is_edit=True,
            submit_label="Save changes",
        )

    @employee_bp.post("/employees/<string:emp_id>/delete")
    @require_auth(auth_service)
    def delete_employee(emp_id: str):
        deleted = employee_service.delete(emp_id)
        if deleted:
            flash("Employee deleted successfully.", "success")
        else:
            flash("Employee not found.", "warning")
        return redirect(url_for("employee.list_employees"))

    return employee_bp
