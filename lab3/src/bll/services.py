from __future__ import annotations

from datetime import date, datetime

from src.dal.interfaces import (
    ICSVReader,
    IEmployeeRepository,
    IEquipmentRepository,
    IHRManagerRepository,
    IITSpecialistRepository,
    IOnboardingProcessRepository,
    ISystemAccountRepository,
    ITrainingModuleRepository,
    IUnitOfWork,
)
from src.dal.models import (
    Employee,
    Equipment,
    HRManager,
    ITSpecialist,
    OnboardingProcess,
    SystemAccount,
    TrainingModule,
)


class OnboardingMigrationService:
    """Migrates flat CSV onboarding records into normalized relational entities."""

    def __init__(
        self,
        csv_reader: ICSVReader,
        uow: IUnitOfWork,
        hr_repo: IHRManagerRepository,
        emp_repo: IEmployeeRepository,
        it_repo: IITSpecialistRepository,
        process_repo: IOnboardingProcessRepository,
        account_repo: ISystemAccountRepository,
        equipment_repo: IEquipmentRepository,
        module_repo: ITrainingModuleRepository,
    ) -> None:
        self._csv_reader = csv_reader
        self._uow = uow
        self._hr_repo = hr_repo
        self._emp_repo = emp_repo
        self._it_repo = it_repo
        self._process_repo = process_repo
        self._account_repo = account_repo
        self._equipment_repo = equipment_repo
        self._module_repo = module_repo

        # Додаємо in-memory кеш (множини) для відстеження унікальних ID під час міграції
        self._processed_hr: set[str] = set()
        self._processed_emp: set[str] = set()
        self._processed_it: set[str] = set()
        self._processed_process: set[str] = set()
        self._processed_account: set[str] = set()
        self._processed_equip: set[str] = set()
        self._processed_module: set[str] = set()

    def migrate(self) -> int:
        inserted_rows = 0
        try:
            for row in self._csv_reader.read_rows():
                self._upsert_hr_manager(row)
                self._upsert_employee(row)
                self._upsert_it_specialist(row)
                self._upsert_onboarding_process(row)
                self._upsert_system_account(row)
                self._upsert_equipment(row)
                self._upsert_training_module(row)
                inserted_rows += 1
            self._uow.commit()
            return inserted_rows
        except Exception:
            self._uow.rollback()
            raise
        finally:
            self._uow.close()

    def _upsert_hr_manager(self, row: dict[str, str]) -> None:
        manager_id = row["managerId"]
        if manager_id in self._processed_hr:
            return
        self._processed_hr.add(manager_id)
        
        if self._hr_repo.get_by_id(manager_id) is None:
            self._hr_repo.add(HRManager(manager_id=manager_id, name=row["managerName"]))

    def _upsert_employee(self, row: dict[str, str]) -> None:
        employee_id = row["employeeId"]
        if employee_id in self._processed_emp:
            return
        self._processed_emp.add(employee_id)

        if self._emp_repo.get_by_id(employee_id) is None:
            self._emp_repo.add(
                Employee(
                    employee_id=employee_id,
                    first_name=row["firstName"],
                    last_name=row["lastName"],
                    email=row["email"],
                    start_date=date.fromisoformat(row["startDate"]),
                    position=row["position"],
                )
            )

    def _upsert_it_specialist(self, row: dict[str, str]) -> None:
        specialist_id = row["specialistId"]
        if specialist_id in self._processed_it:
            return
        self._processed_it.add(specialist_id)

        if self._it_repo.get_by_id(specialist_id) is None:
            self._it_repo.add(
                ITSpecialist(specialist_id=specialist_id, name=row["specialistName"])
            )

    def _upsert_onboarding_process(self, row: dict[str, str]) -> None:
        process_id = row["processId"]
        if process_id in self._processed_process:
            return
        self._processed_process.add(process_id)

        if self._process_repo.get_by_id(process_id) is None:
            self._process_repo.add(
                OnboardingProcess(
                    process_id=process_id,
                    status=row["processStatus"],
                    initiation_date=datetime.fromisoformat(row["initiationDate"]),
                    manager_id=row["managerId"],
                    employee_id=row["employeeId"],
                )
            )

    def _upsert_system_account(self, row: dict[str, str]) -> None:
        account_id = row["accountId"]
        if account_id in self._processed_account:
            return
        self._processed_account.add(account_id)

        if self._account_repo.get_by_id(account_id) is None:
            self._account_repo.add(
                SystemAccount(
                    account_id=account_id,
                    system_name=row["systemName"],
                    username=row["username"],
                    permission_level=row["permissionLevel"],
                    employee_id=row["employeeId"],
                    specialist_id=row["specialistId"],
                )
            )

    def _upsert_equipment(self, row: dict[str, str]) -> None:
        serial_number = row["serialNumber"]
        if serial_number in self._processed_equip:
            return
        self._processed_equip.add(serial_number)

        if self._equipment_repo.get_by_id(serial_number) is None:
            self._equipment_repo.add(
                Equipment(
                    serial_number=serial_number,
                    category=row["equipmentCategory"],
                    model=row["equipmentModel"],
                    status=row["equipmentStatus"],
                    employee_id=row["employeeId"],
                    specialist_id=row["specialistId"],
                )
            )

    def _upsert_training_module(self, row: dict[str, str]) -> None:
        module_id = row["moduleId"]
        if module_id in self._processed_module:
            return
        self._processed_module.add(module_id)

        if self._module_repo.get_by_id(module_id) is None:
            self._module_repo.add(
                TrainingModule(
                    module_id=module_id,
                    title=row["moduleTitle"],
                    is_mandatory=row["isMandatory"].lower() == "true",
                    completion_status=row["completionStatus"],
                    process_id=row["processId"],
                    employee_id=row["employeeId"],
                )
            )