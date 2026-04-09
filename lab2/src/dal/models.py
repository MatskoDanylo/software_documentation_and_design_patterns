from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class HRManager(Base):
    __tablename__ = "hr_managers"

    manager_id: Mapped[str] = mapped_column("managerId", String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)

    onboarding_processes: Mapped[list[OnboardingProcess]] = relationship(
        back_populates="manager", cascade="all,delete-orphan"
    )


class Employee(Base):
    __tablename__ = "employees"

    employee_id: Mapped[str] = mapped_column("employeeId", String(50), primary_key=True)
    first_name: Mapped[str] = mapped_column("firstName", String(80), nullable=False)
    last_name: Mapped[str] = mapped_column("lastName", String(80), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    start_date: Mapped[date] = mapped_column("startDate", Date, nullable=False)
    position: Mapped[str] = mapped_column(String(120), nullable=False)

    onboarding_process: Mapped[OnboardingProcess] = relationship(
        back_populates="employee", uselist=False, cascade="all,delete-orphan"
    )
    system_accounts: Mapped[list[SystemAccount]] = relationship(
        back_populates="employee", cascade="all,delete-orphan"
    )
    equipment_items: Mapped[list[Equipment]] = relationship(
        back_populates="employee", cascade="all,delete-orphan"
    )
    training_modules: Mapped[list[TrainingModule]] = relationship(
        back_populates="employee", cascade="all,delete-orphan"
    )


class ITSpecialist(Base):
    __tablename__ = "it_specialists"

    specialist_id: Mapped[str] = mapped_column("specialistId", String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)

    configured_accounts: Mapped[list[SystemAccount]] = relationship(
        back_populates="it_specialist", cascade="all,delete-orphan"
    )
    prepared_equipment: Mapped[list[Equipment]] = relationship(
        back_populates="it_specialist", cascade="all,delete-orphan"
    )


class OnboardingProcess(Base):
    __tablename__ = "onboarding_processes"

    process_id: Mapped[str] = mapped_column("processId", String(50), primary_key=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    initiation_date: Mapped[datetime] = mapped_column("initiationDate", DateTime, nullable=False)

    manager_id: Mapped[str] = mapped_column(
        "managerId", ForeignKey("hr_managers.managerId"), nullable=False
    )
    employee_id: Mapped[str] = mapped_column(
        "employeeId", ForeignKey("employees.employeeId"), nullable=False, unique=True
    )

    manager: Mapped[HRManager] = relationship(back_populates="onboarding_processes")
    employee: Mapped[Employee] = relationship(back_populates="onboarding_process")
    training_modules: Mapped[list[TrainingModule]] = relationship(
        back_populates="onboarding_process", cascade="all,delete-orphan"
    )


class SystemAccount(Base):
    __tablename__ = "system_accounts"

    account_id: Mapped[str] = mapped_column("accountId", String(50), primary_key=True)
    system_name: Mapped[str] = mapped_column("systemName", String(80), nullable=False)
    username: Mapped[str] = mapped_column(String(120), nullable=False)
    permission_level: Mapped[str] = mapped_column("permissionLevel", String(50), nullable=False)

    employee_id: Mapped[str] = mapped_column(
        "employeeId", ForeignKey("employees.employeeId"), nullable=False
    )
    specialist_id: Mapped[str] = mapped_column(
        "specialistId", ForeignKey("it_specialists.specialistId"), nullable=False
    )

    employee: Mapped[Employee] = relationship(back_populates="system_accounts")
    it_specialist: Mapped[ITSpecialist] = relationship(back_populates="configured_accounts")


class Equipment(Base):
    __tablename__ = "equipment"

    serial_number: Mapped[str] = mapped_column("serialNumber", String(50), primary_key=True)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    model: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)

    employee_id: Mapped[str] = mapped_column(
        "employeeId", ForeignKey("employees.employeeId"), nullable=False
    )
    specialist_id: Mapped[str] = mapped_column(
        "specialistId", ForeignKey("it_specialists.specialistId"), nullable=False
    )

    employee: Mapped[Employee] = relationship(back_populates="equipment_items")
    it_specialist: Mapped[ITSpecialist] = relationship(back_populates="prepared_equipment")


class TrainingModule(Base):
    __tablename__ = "training_modules"

    module_id: Mapped[str] = mapped_column("moduleId", String(50), primary_key=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    is_mandatory: Mapped[bool] = mapped_column("isMandatory", Boolean, nullable=False)
    completion_status: Mapped[str] = mapped_column("completionStatus", String(50), nullable=False)

    process_id: Mapped[str] = mapped_column(
        "processId", ForeignKey("onboarding_processes.processId"), nullable=False
    )
    employee_id: Mapped[str] = mapped_column(
        "employeeId", ForeignKey("employees.employeeId"), nullable=False
    )

    onboarding_process: Mapped[OnboardingProcess] = relationship(back_populates="training_modules")
    employee: Mapped[Employee] = relationship(back_populates="training_modules")

