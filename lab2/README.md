# 3-Tier Onboarding System (Python)

## Lab Assignment

**Laboratory Work 2 — Three-Tier Server-Side Application**

Implement the server-side of an application consisting of three layers:

- **Data Access Layer (DAL)** — responsible for all database interaction and file I/O.
- **Business Logic Layer (BLL)** — orchestrates data flow between DAL and Presentation Layer.
- **Presentation Layer (PL)** — represented by interfaces only; contains no logic at this stage.

**Requirements:**

- Communication between layers must use **interfaces** (BLL classes must depend on DAL interfaces, not concrete implementations), following the **Inversion of Control** and **Dependency Injection** patterns.
- The Presentation Layer is interface-only (`abc.ABC`) and performs no logic.
- The DAL must use an **ORM framework** to populate the database modelled in Lab 1b (class diagram), and must also implement **CSV file reading**.
- The BLL reads data from the CSV via the DAL, constructs the required ORM model instances, normalises them into relational entities, checks for duplicates, and persists them via DAL interfaces.
- All data must reside in a **single flat CSV file**. On import, appropriate logic must handle correct distribution of data across tables.
- The CSV file must contain a **minimum of 1000 rows**.
- A **separate module** must be created for generating the CSV file, runnable from the command line.

---

## Architecture Overview

This project implements a layered architecture:

- **DAL**: SQLAlchemy ORM models, repository interfaces (`abc.ABC`), concrete repositories, and a CSV reader interface with implementation.
- **BLL**: Migration service that reads flat CSV rows, normalises them into relational entities, checks for duplicates, and persists data using DAL interfaces only.
- **PL**: Interface-only layer (`abc.ABC`) for controllers; contains no executable logic.

---

## Project Structure

```text
.
├── data_generator.py       # CLI module for generating flat CSV data
├── main.py                 # Entry point: runs migration from CSV to SQLite
├── requirements.txt
└── src
    ├── bll
    │   └── services.py     # Migration service (BLL)
    ├── dal
    │   ├── csv_reader.py   # CSV reader interface + implementation
    │   ├── db.py           # Database session setup
    │   ├── interfaces.py   # Repository ABCs (used by BLL)
    │   ├── models.py       # SQLAlchemy ORM models
    │   └── repositories.py # Concrete repository implementations
    └── pl
        └── interfaces.py   # Presentation layer interfaces (ABC only)
```

---

## Installation

1. Create and activate a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

### Generate flat CSV data (1000+ rows)

```bash
python data_generator.py
```

Creates `data.csv` in the project root with at least 1000 rows of synthetic onboarding data.

### Run migration to SQLite

```bash
python main.py
```

Creates `onboarding.db`, initialises all tables, and migrates data from `data.csv` — handling normalisation, deduplication, and correct distribution across relational tables.
