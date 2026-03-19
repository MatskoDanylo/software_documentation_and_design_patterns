from __future__ import annotations

import csv
import random
from datetime import datetime
from pathlib import Path

from faker import Faker

OUTPUT_FILE = Path("data.csv")
ROW_COUNT = 1000


def generate_flat_csv(row_count: int = ROW_COUNT, output_file: Path = OUTPUT_FILE) -> None:
    fake = Faker()
    statuses = ["Initiated", "InProgress", "Completed"]
    permissions = ["Read", "Write", "Admin"]
    equipment_categories = ["Laptop", "Phone", "Monitor", "Headset"]
    equipment_statuses = ["Prepared", "Assigned", "Delivered"]
    modules = ["Security Training", "HR Policies", "Code of Conduct", "System Access Intro"]

    fieldnames = [
        "managerId",
        "managerName",
        "employeeId",
        "firstName",
        "lastName",
        "email",
        "startDate",
        "position",
        "specialistId",
        "specialistName",
        "processId",
        "processStatus",
        "initiationDate",
        "accountId",
        "systemName",
        "username",
        "permissionLevel",
        "serialNumber",
        "equipmentCategory",
        "equipmentModel",
        "equipmentStatus",
        "moduleId",
        "moduleTitle",
        "isMandatory",
        "completionStatus",
    ]

    with output_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(1, row_count + 1):
            first_name = fake.first_name()
            last_name = fake.last_name()
            start_date = fake.date_between(start_date="-90d", end_date="+60d")
            initiation_date = datetime.combine(start_date, datetime.min.time())
            system_name = random.choice(["Jira", "GitHub", "Slack", "Confluence", "Email"])
            row = {
                "managerId": f"M{(i % 50) + 1:03d}",
                "managerName": fake.name(),
                "employeeId": f"E{i:05d}",
                "firstName": first_name,
                "lastName": last_name,
                "email": f"{first_name.lower()}.{last_name.lower()}.{i}@example.com",
                "startDate": start_date.isoformat(),
                "position": fake.job(),
                "specialistId": f"S{(i % 60) + 1:03d}",
                "specialistName": fake.name(),
                "processId": f"P{i:05d}",
                "processStatus": random.choice(statuses),
                "initiationDate": initiation_date.isoformat(),
                "accountId": f"A{i:05d}",
                "systemName": system_name,
                "username": f"{first_name.lower()}.{last_name.lower()}{i}",
                "permissionLevel": random.choice(permissions),
                "serialNumber": f"SN{i:06d}",
                "equipmentCategory": random.choice(equipment_categories),
                "equipmentModel": f"{fake.word().capitalize()}-{random.randint(100, 999)}",
                "equipmentStatus": random.choice(equipment_statuses),
                "moduleId": f"T{i:05d}",
                "moduleTitle": random.choice(modules),
                "isMandatory": str(random.choice([True, False])),
                "completionStatus": random.choice(["NotStarted", "InProgress", "Completed"]),
            }
            writer.writerow(row)

    print(f"Generated {row_count} rows in {output_file}")


if __name__ == "__main__":
    generate_flat_csv()

