"""
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
    """