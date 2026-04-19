from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from .models import (
    Employee,
    Equipment,
    HRManager,
    ITSpecialist,
    OnboardingProcess,
    SystemAccount,
    TrainingModule,
)


class ICSVReader(ABC):
    @abstractmethod
    def read_rows(self) -> Iterable[dict[str, str]]:
        """Read flat rows from CSV."""


class IUnitOfWork(ABC):
    @abstractmethod
    def commit(self) -> None:
        """Commit current transaction."""

    @abstractmethod
    def rollback(self) -> None:
        """Rollback current transaction."""

    @abstractmethod
    def close(self) -> None:
        """Close current session/resources."""


class IHRManagerRepository(ABC):
    @abstractmethod
    def get_by_id(self, manager_id: str) -> HRManager | None:
        pass

    @abstractmethod
    def add(self, manager: HRManager) -> None:
        pass


class IEmployeeRepository(ABC):
    @abstractmethod
    def get_by_id(self, employee_id: str) -> Employee | None:
        pass

    @abstractmethod
    def add(self, employee: Employee) -> None:
        pass


class IITSpecialistRepository(ABC):
    @abstractmethod
    def get_by_id(self, specialist_id: str) -> ITSpecialist | None:
        pass

    @abstractmethod
    def add(self, specialist: ITSpecialist) -> None:
        pass


class IOnboardingProcessRepository(ABC):
    @abstractmethod
    def get_by_id(self, process_id: str) -> OnboardingProcess | None:
        pass

    @abstractmethod
    def add(self, process: OnboardingProcess) -> None:
        pass


class ISystemAccountRepository(ABC):
    @abstractmethod
    def get_by_id(self, account_id: str) -> SystemAccount | None:
        pass

    @abstractmethod
    def add(self, account: SystemAccount) -> None:
        pass


class IEquipmentRepository(ABC):
    @abstractmethod
    def get_by_id(self, serial_number: str) -> Equipment | None:
        pass

    @abstractmethod
    def add(self, equipment: Equipment) -> None:
        pass


class ITrainingModuleRepository(ABC):
    @abstractmethod
    def get_by_id(self, module_id: str) -> TrainingModule | None:
        pass

    @abstractmethod
    def add(self, module: TrainingModule) -> None:
        pass

