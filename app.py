

from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from datetime import datetime

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "medwaste.db")

app = Flask(__name__)
app.secret_key = "medwaste-mini-project-secret-key"

WASTE_CATEGORIES = {
    "Infectious Waste":            {"color": "Yellow", "hex": "#FFC107"},
    "Pathological / Anatomical":   {"color": "Yellow", "hex": "#FFC107"},
    "Sharps (Needles/Syringes)":   {"color": "White",  "hex": "#F5F5F5"},
    "Contaminated Recyclables":    {"color": "Red",    "hex": "#E53935"},
    "General Non-Hazardous":       {"color": "Black",  "hex": "#424242"},
    "Glassware / Metal":           {"color": "Blue",   "hex": "#1E88E5"},
    "Chemical / Pharmaceutical":   {"color": "Brown",  "hex": "#8D6E63"},
}



def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS waste_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            waste_category TEXT NOT NULL,
            bin_color TEXT NOT NULL,
            quantity_kg REAL NOT NULL,
            source_location TEXT NOT NULL,
            collector_staff_id TEXT NOT NULL,
            collector_name TEXT NOT NULL,
            disposer_staff_id TEXT NOT NULL,
            disposer_name TEXT NOT NULL,
            disposal_location TEXT,
            record_datetime TEXT NOT NULL,
            remarks TEXT
        )
    """)
    
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(waste_records)")}
    if "disposal_location" not in columns:
        conn.execute("ALTER TABLE waste_records ADD COLUMN disposal_location TEXT")
    conn.commit()
    conn.close()


@app.route("/")
def dashboard():
    conn = get_db()
    records = conn.execute(
        "SELECT * FROM waste_records ORDER BY id DESC LIMIT 5"
    ).fetchall()

    total_records = conn.execute("SELECT COUNT(*) c FROM waste_records").fetchone()["c"]
    total_qty = conn.execute("SELECT COALESCE(SUM(quantity_kg),0) s FROM waste_records").fetchone()["s"]

    by_category = conn.execute("""
        SELECT waste_category, bin_color, COUNT(*) cnt, COALESCE(SUM(quantity_kg),0) qty
        FROM waste_records
        GROUP BY waste_category, bin_color
        ORDER BY qty DESC
    """).fetchall()
    conn.close()

    return render_template(
        "index.html",
        records=records,
        total_records=total_records,
        total_qty=round(total_qty, 2),
        by_category=by_category,
        categories=WASTE_CATEGORIES,
    )


@app.route("/add", methods=["GET", "POST"])
def add_record():
    if request.method == "POST":
        waste_category = request.form.get("waste_category")
        quantity_kg = request.form.get("quantity_kg")
        source_location = request.form.get("source_location", "").strip()
        collector_staff_id = request.form.get("collector_staff_id", "").strip()
        collector_name = request.form.get("collector_name", "").strip()
        disposer_staff_id = request.form.get("disposer_staff_id", "").strip()
        disposer_name = request.form.get("disposer_name", "").strip()
        disposal_location = request.form.get("disposal_location", "").strip()
        remarks = request.form.get("remarks", "").strip()

        if not all([waste_category, quantity_kg, source_location,
                    collector_staff_id, collector_name,
                    disposer_staff_id, disposer_name, disposal_location]):
            flash("Please fill in all required fields.", "error")
            return redirect(url_for("add_record"))

        try:
            quantity_kg = float(quantity_kg)
            if quantity_kg <= 0:
                raise ValueError
        except ValueError:
            flash("Quantity must be a positive number.", "error")
            return redirect(url_for("add_record"))

        bin_color = WASTE_CATEGORIES.get(waste_category, {}).get("color", "Unknown")
        record_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = get_db()
        conn.execute("""
            INSERT INTO waste_records
            (waste_category, bin_color, quantity_kg, source_location,
             collector_staff_id, collector_name, disposer_staff_id, disposer_name,
             disposal_location, record_datetime, remarks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (waste_category, bin_color, quantity_kg, source_location,
              collector_staff_id, collector_name, disposer_staff_id, disposer_name,
              disposal_location, record_datetime, remarks))
        conn.commit()
        conn.close()

        flash("Waste record added successfully!", "success")
        return redirect(url_for("records"))

    return render_template("add.html", categories=WASTE_CATEGORIES)


@app.route("/records")
def records():
    conn = get_db()
    search = request.args.get("q", "").strip()
    if search:
        like = f"%{search}%"
        rows = conn.execute("""
            SELECT * FROM waste_records
            WHERE waste_category LIKE ? OR collector_staff_id LIKE ?
               OR disposer_staff_id LIKE ? OR source_location LIKE ?
               OR disposal_location LIKE ? OR collector_name LIKE ? OR disposer_name LIKE ?
            ORDER BY id DESC
        """, (like, like, like, like, like, like, like)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM waste_records ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("records.html", records=rows, categories=WASTE_CATEGORIES, search=search)


@app.route("/delete/<int:record_id>", methods=["POST"])
def delete_record(record_id):
    conn = get_db()
    conn.execute("DELETE FROM waste_records WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()
    flash("Record deleted.", "success")
    return redirect(url_for("records"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
