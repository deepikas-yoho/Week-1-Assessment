from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CHARTS = ROOT / "reports" / "charts"
CHARTS.mkdir(parents=True, exist_ok=True)

# Part A: NumPy
marks = np.array([
    [80, 75, 90],
    [65, 70, 72],
    [90, 88, 95],
    [78, 82, 85],
])

print("Marks shape:", marks.shape)
print("Student averages:", marks.mean(axis=1))
print("Subject averages:", marks.mean(axis=0))

grace_marks = marks + 5
print("Marks after grace:", grace_marks)

weights = np.array([0.3, 0.3, 0.4])
weighted_scores = np.dot(marks, weights)
print("Weighted scores:", weighted_scores)

# Part B: Load and inspect the original employee data.
employees = pd.read_csv(DATA / "employees.csv")
print("\nDataFrame info:")
employees.info()
print("\nDescriptive statistics:")
print(employees.describe())

print("\nUsing loc:")
print(employees.loc[employees["salary"] > 50000, ["name", "salary"]])

print("\nUsing iloc:")
print(employees.iloc[:3])

print("\nIT employees:")
print(employees[employees["department"] == "IT"])

# Part C: Create a separate intentionally dirty dataset.
dirty = pd.read_csv(DATA / "employees.csv")
dirty.loc[dirty["id"].isin([2, 6]), "salary"] = np.nan
dirty = pd.concat([dirty, dirty.iloc[[0]]], ignore_index=True)
dirty.to_csv(DATA / "employees_dirty.csv", index=False)

cleaned = pd.read_csv(DATA / "employees_dirty.csv")
cleaned["salary"] = pd.to_numeric(cleaned["salary"], errors="coerce")
cleaned["id"] = pd.to_numeric(cleaned["id"], errors="coerce").astype("Int64")

duplicate_count = int(cleaned.duplicated().sum())
cleaned = cleaned.drop_duplicates().copy()

missing_count = int(cleaned["salary"].isna().sum())
median_salary = cleaned["salary"].median()
cleaned["salary"] = cleaned["salary"].fillna(median_salary)
cleaned["salary"] = cleaned["salary"].astype(float)

print("\nDuplicate rows removed:", duplicate_count)
print("Missing salaries filled:", missing_count)
print("Median used:", median_salary)
cleaned.to_csv(DATA / "employees_cleaned.csv", index=False)

# Part D: Department summaries.
summary = cleaned.groupby("department").agg(
    headcount=("id", "count"),
    average_salary=("salary", "mean"),
    maximum_salary=("salary", "max"),
).reset_index()

print("\nDepartment summary:")
print(summary.round(2).to_string(index=False))

departments = pd.read_csv(DATA / "departments.csv")

print("\nInner join:")
print(cleaned.merge(departments, on="department", how="inner"))

print("\nLeft join:")
print(cleaned.merge(departments, on="department", how="left"))

outer = cleaned.merge(departments, on="department", how="outer", indicator=True)
print("\nOuter join:")
print(outer[["department", "name", "_merge"]].to_string(index=False))

employee_departments = set(cleaned["department"].dropna())
empty_departments = sorted(
    set(departments["department"]) - employee_departments
)
print("Departments with no employees:", empty_departments)

# Part E: Four charts saved as PNG files.
# 1. Bar chart: headcount by department.
fig, ax = plt.subplots()
ax.bar(summary["department"], summary["headcount"], label="Employees")
ax.set(title="Employee Headcount by Department",
       xlabel="Department", ylabel="Headcount")
ax.legend()
fig.tight_layout()
fig.savefig(CHARTS / "department_headcount.png", dpi=150)
plt.close(fig)
print("Insight: IT has the largest headcount in the supplied employee data.")

# 2. Histogram: salary distribution.
fig, ax = plt.subplots()
ax.hist(cleaned["salary"], bins=5, edgecolor="black", label="Employees")
ax.set(title="Employee Salary Distribution",
       xlabel="Salary", ylabel="Number of Employees")
ax.legend()
fig.tight_layout()
fig.savefig(CHARTS / "salary_histogram.png", dpi=150)
plt.close(fig)
print("Insight: The histogram shows how employee salaries are distributed across salary ranges.")

# 3. Scatter chart: salary by employee.
fig, ax = plt.subplots()
ax.scatter(cleaned["name"], cleaned["salary"], label="Salary", color="teal")
ax.set(title="Salary by Employee",
       xlabel="Employee", ylabel="Salary")
ax.tick_params(axis="x", rotation=45)
ax.legend()
fig.tight_layout()
fig.savefig(CHARTS / "salary_scatter.png", dpi=150)
plt.close(fig)
print("Insight: The scatter chart highlights salary differences between individual employees.")

# 4. Line chart: salary by employee ID.
ordered = cleaned.sort_values("id")
fig, ax = plt.subplots()
ax.plot(ordered["id"], ordered["salary"], marker="o", label="Salary")
ax.set(title="Salary by Employee ID",
       xlabel="Employee ID", ylabel="Salary")
ax.legend()
fig.tight_layout()
fig.savefig(CHARTS / "salary_line.png", dpi=150)
plt.close(fig)
print("Insight: The line chart shows salary variation across employee IDs.")

print("\nCharts saved to:", CHARTS)