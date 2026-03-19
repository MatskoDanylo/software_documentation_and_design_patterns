Software documentation and design patterns

## 3-Tier Onboarding System (Python)

This project implements a layered architecture:
- **DAL**: SQLAlchemy ORM models, repository interfaces (ABC), concrete repositories, and CSV reader interface/implementation.
- **BLL**: Migration service that reads flat CSV rows, normalizes to relational entities, checks duplicates, and persists using DAL interfaces only.
- **PL**: Interface-only layer (`abc.ABC`) for controllers.

### Project structure

```text
.
├── data_generator.py
├── main.py
├── requirements.txt
└── src
    ├── bll
    │   └── services.py
    ├── dal
    │   ├── csv_reader.py
    │   ├── db.py
    │   ├── interfaces.py
    │   ├── models.py
    │   └── repositories.py
    └── pl
        └── interfaces.py
```

### Installation

1. Create and activate a virtual environment (recommended).
2. Install dependencies:

```bash
pip install -r requirements.txt
```

### Generate flat CSV data (1000 rows)

```bash
python data_generator.py
```

This creates `data.csv` in the project root.

### Run migration to SQLite

```bash
python main.py
```

This creates `onboarding.db`, creates tables, and migrates data from `data.csv`.
