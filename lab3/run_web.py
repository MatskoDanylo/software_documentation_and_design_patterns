from __future__ import annotations

from src.bll.employee_service import EmployeeService
from src.dal.db import Base, create_session_factory, create_sqlite_engine
from src.dal.repositories import EmployeeRepository, SQLAlchemyUnitOfWork
from src.pl.app import create_app


def main() -> None:
    # Composition root: wiring concrete DAL to BLL and PL.
    engine = create_sqlite_engine("onboarding.db")
    Base.metadata.create_all(engine)

    session_factory = create_session_factory(engine)
    session = session_factory()

    employee_repository = EmployeeRepository(session)
    uow = SQLAlchemyUnitOfWork(session)
    employee_service = EmployeeService(employee_repository=employee_repository, uow=uow)

    app = create_app(employee_service)

    try:
        app.run(debug=True)
    finally:
        uow.close()


if __name__ == "__main__":
    main()
