import csv
import os
from datetime import datetime
from flask import Flask, jsonify, request, send_file, send_from_directory

app = Flask(__name__, static_folder=".", static_url_path="")
FILE_NAME = "expenses.csv"


def ensure_csv_exists():
    """Ensure the CSV file exists with proper headers."""
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Category", "Description", "Amount"])


def read_expenses_from_csv():
    """Read all rows from the CSV file as a list of dicts with unique IDs."""
    ensure_csv_exists()
    expenses = []
    with open(FILE_NAME, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for idx, row in enumerate(reader):
            if row and any(row.values()):
                try:
                    amount = float(row.get("Amount", 0))
                except (ValueError, TypeError):
                    amount = 0.0

                expenses.append({
                    "id": idx,
                    "date": row.get("Date", "").strip(),
                    "category": row.get("Category", "").strip(),
                    "description": row.get("Description", "").strip(),
                    "amount": amount
                })
    return expenses


def write_expenses_to_csv(expenses):
    """Write list of expenses back to CSV file."""
    with open(FILE_NAME, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Category", "Description", "Amount"])
        for exp in expenses:
            writer.writerow([
                exp.get("date", ""),
                exp.get("category", ""),
                exp.get("description", ""),
                f"{float(exp.get('amount', 0)):.2f}"
            ])


@app.route("/")
def index():
    """Serve the main web frontend."""
    return send_from_directory(".", "index.html")


@app.route("/api/expenses", methods=["GET"])
def get_expenses():
    """Return all expenses as JSON."""
    expenses = read_expenses_from_csv()
    return jsonify({"success": True, "expenses": expenses})


@app.route("/api/expenses", methods=["POST"])
def add_expense():
    """Add a new expense to CSV."""
    data = request.get_json() or {}
    category = data.get("category", "").strip()
    description = data.get("description", "").strip()
    amount_raw = data.get("amount")
    date_str = data.get("date", "").strip()

    if not category:
        return jsonify({"success": False, "error": "Category is required."}), 400
    if not description:
        return jsonify({"success": False, "error": "Description is required."}), 400

    try:
        amount = float(amount_raw)
        if amount <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Amount must be a positive number."}), 400

    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    ensure_csv_exists()
    with open(FILE_NAME, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([date_str, category, description, f"{amount:.2f}"])

    return jsonify({"success": True, "message": "Expense added successfully!"}), 201


@app.route("/api/expenses/<int:item_id>", methods=["DELETE"])
def delete_expense(item_id):
    """Delete an expense by index from CSV."""
    expenses = read_expenses_from_csv()
    if item_id < 0 or item_id >= len(expenses):
        return jsonify({"success": False, "error": "Expense not found."}), 404

    expenses.pop(item_id)
    write_expenses_to_csv(expenses)
    return jsonify({"success": True, "message": "Expense deleted successfully!"})


@app.route("/api/expenses/clear", methods=["POST"])
def clear_all_expenses():
    """Clear all expenses while retaining the CSV header."""
    with open(FILE_NAME, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Category", "Description", "Amount"])
    return jsonify({"success": True, "message": "All expenses cleared."})


@app.route("/api/summary", methods=["GET"])
def get_summary():
    """Return category summary, monthly breakdown, and totals."""
    expenses = read_expenses_from_csv()
    category_totals = {}
    monthly_totals = {}
    total_amount = 0.0

    for exp in expenses:
        amt = exp["amount"]
        cat = exp["category"]
        date_str = exp["date"]

        total_amount += amt
        category_totals[cat] = category_totals.get(cat, 0.0) + amt

        month_key = date_str[:7] if len(date_str) >= 7 else "Unknown"
        monthly_totals[month_key] = monthly_totals.get(month_key, 0.0) + amt

    top_category = "-"
    if category_totals:
        top_category = max(category_totals.items(), key=lambda x: x[1])[0]

    return jsonify({
        "success": True,
        "total_amount": round(total_amount, 2),
        "total_transactions": len(expenses),
        "top_category": top_category,
        "category_totals": {k: round(v, 2) for k, v in category_totals.items()},
        "monthly_totals": {k: round(v, 2) for k, v in sorted(monthly_totals.items())}
    })


@app.route("/api/export", methods=["GET"])
def export_csv():
    """Download the actual CSV file."""
    ensure_csv_exists()
    return send_file(FILE_NAME, as_attachment=True, download_name="expenses.csv")


if __name__ == "__main__":
    ensure_csv_exists()
    print("==================================================")
    print(" Personal Expense Tracker - College Mini Project ")
    print(" Running at: http://127.0.0.1:5000")
    print(" Press Ctrl+C to stop.")
    print("==================================================")
    app.run(debug=True, port=5000)
