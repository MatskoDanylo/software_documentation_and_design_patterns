from __future__ import annotations

from sqlalchemy.orm import Session

from .interfaces import (
    IEmployeeRepository,
    IEquipmentRepository,
    IHRManagerRepository,
    IITSpecialistRepository,
    IOnboardingProcessRepository,
    ISystemAccountRepository,
    ITrainingModuleRepository,
    IUnitOfWork,
)
from .models import (
    Employee,
    Equipment,
    HRManager,
    ITSpecialist,
    OnboardingProcess,
    SystemAccount,
    TrainingModule,
)


class SQLAlchemyUnitOfWork(IUnitOfWork):
    def __init__(self, session: Session) -> None:
        self._session = session

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()

    def close(self) -> None:
        self._session.close()


class HRManagerRepository(IHRManagerRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, manager_id: str) -> HRManager | None:
        return self._session.get(HRManager, manager_id)

    def add(self, manager: HRManager) -> None:
        self._session.add(manager)


class EmployeeRepository(IEmployeeRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, employee_id: str) -> Employee | None:
        return self._session.get(Employee, employee_id)

    def add(self, employee: Employee) -> None:
        self._session.add(employee)


class ITSpecialistRepository(IITSpecialistRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, specialist_id: str) -> ITSpecialist | None:
        return self._session.get(ITSpecialist, specialist_id)

    def add(self, specialist: ITSpecialist) -> None:
        self._session.add(specialist)


class OnboardingProcessRepository(IOnboardingProcessRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, process_id: str) -> OnboardingProcess | None:
        return self._session.get(OnboardingProcess, process_id)

    def add(self, process: OnboardingProcess) -> None:
        self._session.add(process)


class SystemAccountRepository(ISystemAccountRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, account_id: str) -> SystemAccount | None:
        return self._session.get(SystemAccount, account_id)

    def add(self, account: SystemAccount) -> None:
        self._session.add(account)


class EquipmentRepository(IEquipmentRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, serial_number: str) -> Equipment | None:
        return self._session.get(Equipment, serial_number)

    def add(self, equipment: Equipment) -> None:
        self._session.add(equipment)


class TrainingModuleRepository(ITrainingModuleRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, module_id: str) -> TrainingModule | None:
        return self._session.get(TrainingModule, module_id)

    def add(self, module: TrainingModule) -> None:
        self._session.add(module)

