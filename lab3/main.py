from src.bll.services import OnboardingMigrationService
from src.dal.csv_reader import FlatCSVReader
from src.dal.db import Base, create_session_factory, create_sqlite_engine
from src.dal.repositories import (
    EmployeeRepository,
    EquipmentRepository,
    HRManagerRepository,
    ITSpecialistRepository,
    OnboardingProcessRepository,
    SQLAlchemyUnitOfWork,
    SystemAccountRepository,
    TrainingModuleRepository,
)


def main() -> None:
    # Manual dependency composition root (IoC + DI)
    engine = create_sqlite_engine("onboarding.db")
    Base.metadata.create_all(engine)
    session = create_session_factory(engine)()

    csv_reader = FlatCSVReader("data.csv")
    uow = SQLAlchemyUnitOfWork(session)

    service = OnboardingMigrationService(
        csv_reader=csv_reader,
        uow=uow,
        hr_repo=HRManagerRepository(session),
        emp_repo=EmployeeRepository(session),
        it_repo=ITSpecialistRepository(session),
        process_repo=OnboardingProcessRepository(session),
        account_repo=SystemAccountRepository(session),
        equipment_repo=EquipmentRepository(session),
        module_repo=TrainingModuleRepository(session),
    )

    migrated_rows = service.migrate()
    print(f"Migration complete. Processed {migrated_rows} CSV rows.")


if __name__ == "__main__":
    main()

