import csv
import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

# Project paths
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)

# Load environment variables from the project root.
load_dotenv(ROOT / ".env")
api_key = os.getenv("API_KEY")
print("API key configured:", bool(api_key))

# --------------------------------------------------
# 1. Read employees.csv and write employees.json
# --------------------------------------------------

csv_path = DATA / "employees.csv"

with csv_path.open(
    "r", newline="", encoding="utf-8-sig"
) as file:
    reader = csv.DictReader(file)

    # Validate and normalize CSV column names.
    if reader.fieldnames:
        reader.fieldnames = [
            name.strip() for name in reader.fieldnames
        ]

    expected_columns = {
        "id", "name", "department", "salary", "city"
    }

    if not reader.fieldnames or not expected_columns.issubset(
        reader.fieldnames
    ):
        raise ValueError(
            f"Invalid CSV headers: {reader.fieldnames}. "
            f"Expected columns: {sorted(expected_columns)}"
        )

    employees = list(reader)

if not employees:
    raise ValueError(f"No employee records found in {csv_path}")

# Convert CSV strings to suitable numeric types.
for employee in employees:
    employee["id"] = int(employee["id"])
    employee["salary"] = float(employee["salary"])

# Write all employees to JSON.
with (DATA / "employees.json").open(
    "w", encoding="utf-8"
) as file:
    json.dump(employees, file, indent=2)

# --------------------------------------------------
# 2. Write high_earners.csv
# --------------------------------------------------

high_earners = [
    employee
    for employee in employees
    if employee["salary"] > 50000
]

with (DATA / "high_earners.csv").open(
    "w", newline="", encoding="utf-8"
) as file:
    writer = csv.DictWriter(
        file, fieldnames=employees[0].keys()
    )
    writer.writeheader()
    writer.writerows(high_earners)

print(
    f"Rows read: {len(employees)} | "
    f"High earners: {len(high_earners)}"
)

# --------------------------------------------------
# 3. REST API: GET users
# --------------------------------------------------

BASE_URL = "https://jsonplaceholder.typicode.com"


def get_users():
    """Fetch users, display the first three, and save nested JSON."""
    try:
        response = requests.get(
            f"{BASE_URL}/users", timeout=5
        )
        response.raise_for_status()
        users = response.json()

        for user in users[:3]:
            print(
                f'{user.get("id")} - '
                f'{user.get("name")} - '
                f'{user.get("email")}'
            )

        # Safely extract nested address and company fields.
        selected_users = [
            {
                "id": user.get("id"),
                "name": user.get("name"),
                "email": user.get("email"),
                "city": user.get("address", {}).get("city"),
                "company": user.get("company", {}).get("name"),
            }
            for user in users
        ]

        with (DATA / "users.json").open(
            "w", encoding="utf-8"
        ) as file:
            json.dump(selected_users, file, indent=2)

        print("users.json saved successfully.")

    except requests.exceptions.Timeout:
        print("API request timed out.")
    except requests.exceptions.ConnectionError:
        print("Could not connect to the API.")
    except requests.exceptions.HTTPError as error:
        print("HTTP error:", error)
    except requests.exceptions.RequestException as error:
        print("API request failed:", error)
    except ValueError as error:
        print("Invalid API response:", error)


# --------------------------------------------------
# 4. Demonstrate HTTP 404 for /users/9999
# --------------------------------------------------

def check_missing_user():
    try:
        response = requests.get(
            f"{BASE_URL}/users/9999", timeout=5
        )

        if response.status_code == 404:
            print("/users/9999 -> 404 Not found")
        else:
            response.raise_for_status()
            print("Unexpected response:", response.status_code)

    except requests.exceptions.Timeout:
        print("404 test request timed out.")
    except requests.exceptions.ConnectionError:
        print("Could not connect during 404 test.")
    except requests.exceptions.HTTPError as error:
        print("HTTP error during 404 test:", error)
    except requests.exceptions.RequestException as error:
        print("404 test request failed:", error)


if __name__ == "__main__":
    get_users()
    check_missing_user()
