# SAP SuccessFactors Onboarding System (Python)

## Laboratory Work 3: MVC Web Application

This project extends the strict 3-tier architecture from Lab 2 by implementing a Flask-based MVC web interface for Employee CRUD operations.

Domain: SAP SuccessFactors People Onboarding  
Target entity: Employee

## Key Technologies

- Python 3.10+
- SQLAlchemy 2.x (SQLite)
- Flask 3.x
- Repository Pattern
- Unit of Work Pattern
- Dependency Injection

## Architecture (Strict 3-Tier)

### DAL (Data Access Layer)

- SQLAlchemy ORM models and DB session setup
- Repository interfaces and concrete implementations
- Unit of Work abstraction and implementation
- CSV data import support from Lab 2

### BLL (Business Logic Layer)

- Migration service from Lab 2
- Employee CRUD business service (`EmployeeService`)
- Operates via DAL interfaces, not concrete persistence details

### PL (Presentation Layer, MVC)

- Flask app factory (`create_app(employee_service)`)
- Controllers implemented as Flask Blueprints
- Jinja2 templates for list/form views
- No direct DB/session access from controllers

## Architectural Rules Enforced

1. Controllers do not import or use SQLAlchemy `Session`, DAL models, or concrete repositories.
2. Controllers communicate only with BLL (`EmployeeService`).
3. `EmployeeService` works through `IEmployeeRepository` and `IUnitOfWork`.
4. Composition root wires dependencies and injects service into the Flask app.

## Project Structure

```text
.
├── data_generator.py
├── main.py                           # Lab 2 migration entry point
├── run_web.py                        # Lab 3 web composition root
├── requirements.txt
└── src
    ├── bll
    │   ├── services.py               # Migration service (Lab 2)
    │   └── employee_service.py       # Employee CRUD business service
    ├── dal
    │   ├── csv_reader.py
    │   ├── db.py
    │   ├── interfaces.py
    │   ├── models.py
    │   └── repositories.py
    └── pl
        ├── app.py                    # Flask app factory
        ├── controllers
        │   └── employee_controller.py
        └── templates
            ├── base.html
            ├── employee_list.html
            └── employee_form.html
```

## Installation

1. Create and activate a virtual environment:

```bash
python -m venv .venv
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### 1) Generate source CSV data (optional)

```bash
python data_generator.py
```

### 2) Run Lab 2 migration (optional if DB already seeded)

```bash
python main.py
```

### 3) Run Lab 3 web application

```bash
python run_web.py
```

Open the app in your browser (default Flask URL):

```text
http://127.0.0.1:5000/employees
```

## Employee Web Features

- View all employees
- Create employee
- Edit employee
- Delete employee

## Web Routes

- `GET /` -> redirect to `/employees`
- `GET /employees` -> employee list
- `GET, POST /employees/create` -> create employee
- `GET, POST /employees/<emp_id>/edit` -> edit employee
- `POST /employees/<emp_id>/delete` -> delete employee

## Notes

- SQLite database file: `onboarding.db`
- Templates use Bootstrap 5 CDN for UI styling
- If Flask import errors appear in IDE, ensure the correct virtual environment is selected and dependencies are installed
