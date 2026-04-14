from __future__ import annotations

from datetime import date

from src.dal.interfaces import IEmployeeRepository, IUnitOfWork
from src.dal.models import Employee


class EmployeeService:
    """Business service for Employee CRUD operations."""

    def __init__(self, employee_repository: IEmployeeRepository, uow: IUnitOfWork) -> None:
        self._employee_repository = employee_repository
        self._uow = uow

    def get_all(self) -> list[Employee]:
        return self._employee_repository.get_all()

    def get_by_id(self, emp_id: str) -> Employee | None:
        return self._employee_repository.get_by_id(emp_id)

    def create(self, data: dict[str, str]) -> Employee:
        employee_id = (data.get("employee_id") or "").strip()
        if not employee_id:
            raise ValueError("Employee ID is required")

        if self._employee_repository.get_by_id(employee_id) is not None:
            raise ValueError(f"Employee with ID '{employee_id}' already exists")

        email = (data.get("email") or "").strip()
        if not email:
            raise ValueError("Email is required")

        start_date_raw = (data.get("start_date") or "").strip()
        if not start_date_raw:
            raise ValueError("Start date is required")

        employee = Employee(
            employee_id=employee_id,
            first_name=(data.get("first_name") or "").strip(),
            last_name=(data.get("last_name") or "").strip(),
            email=email,
            start_date=date.fromisoformat(start_date_raw),
            position=(data.get("position") or "").strip(),
        )

        if not employee.first_name:
            raise ValueError("First name is required")
        if not employee.last_name:
            raise ValueError("Last name is required")
        if not employee.position:
            raise ValueError("Position is required")

        try:
            self._employee_repository.add(employee)
            self._uow.commit()
            return employee
        except Exception:
            self._uow.rollback()
            raise

    def update(self, emp_id: str, data: dict[str, str]) -> Employee:
        employee = self._employee_repository.get_by_id(emp_id)
        if employee is None:
            raise ValueError(f"Employee with ID '{emp_id}' was not found")

        first_name = (data.get("first_name") or "").strip()
        last_name = (data.get("last_name") or "").strip()
        email = (data.get("email") or "").strip()
        start_date_raw = (data.get("start_date") or "").strip()
        position = (data.get("position") or "").strip()

        if not first_name:
            raise ValueError("First name is required")
        if not last_name:
            raise ValueError("Last name is required")
        if not email:
            raise ValueError("Email is required")
        if not start_date_raw:
            raise ValueError("Start date is required")
        if not position:
            raise ValueError("Position is required")

        employee.first_name = first_name
        employee.last_name = last_name
        employee.email = email
        employee.start_date = date.fromisoformat(start_date_raw)
        employee.position = position

        try:
            self._uow.commit()
            return employee
        except Exception:
            self._uow.rollback()
            raise

    def delete(self, emp_id: str) -> bool:
        try:
            deleted = self._employee_repository.delete_by_id(emp_id)
            if not deleted:
                return False
            self._uow.commit()
            return True
        except Exception:
            self._uow.rollback()
            raise
