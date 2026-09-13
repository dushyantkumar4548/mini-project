"""
MedWaste Tracker - Biomedical Waste Management Mini Project
-------------------------------------------------------------
A simple desktop application (Tkinter) for a college mini project.

Features:
1. Waste Segregation      - pick a waste type, see the correct bin
2. Add Waste Bag          - create a new waste bag record
3. Records                - view / search / delete waste bag records
4. Custody Tracking       - log handoff of a bag between staff / locations
5. Reports                - view waste composition summary & export as CSV

Data is stored in a local JSON file (waste_data.json) so records are
not lost when the application is closed and reopened.

Only Python's standard library is used (tkinter, json, csv, datetime, os)
so it will run on any machine with Python 3 installed - no extra
packages need to be installed.
"""

import json
import csv
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox


DATA_FILE = "waste_data.json"

# Waste type -> (Bin Colour, Description)
WASTE_TYPES = {
    "Infectious Waste":     ("Yellow Bin", "Infectious / contaminated biomedical waste."),
    "Sharps":               ("White Bin",  "Needles, blades and other sharp items."),
    "Glass":                ("White Bin",  "Contaminated glass waste."),
    "Disposable":           ("Blue Bin",   "Recyclable contaminated disposable items."),
    "Pharmaceutical":       ("Yellow Bin", "Expired / unused medicines."),
    "Chemical":             ("Black Bin",  "Chemical / hazardous waste."),
    "General Waste":        ("Green Bin",  "Non-biomedical general waste."),
}

# Bin colour name -> actual colour used to highlight it in the interface
BIN_COLOR_MAP = {
    "Yellow Bin": "#f6c90e",
    "White Bin":  "#e5e7eb",
    "Blue Bin":   "#3b82f6",
    "Black Bin":  "#374151",
    "Green Bin":  "#22c55e",
}

# ---------------------------------------------------------------
# Simple colour theme for the whole application
# ---------------------------------------------------------------
COLORS = {
    "primary":      "#0e7c66",   # teal-green - main brand colour
    "primary_dark": "#0a5c4b",
    "accent":       "#f59e0b",   # amber - used for warnings / secondary buttons
    "danger":       "#dc2626",
    "bg":           "#eef6f3",   # light page background
    "card":         "#ffffff",
    "text":         "#1f2937",
    "muted":        "#6b7280",
}


class MedWasteApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MedWaste Tracker - Biomedical Waste Management System")
        self.geometry("950x650")
        self.minsize(850, 580)
        self.configure(bg=COLORS["bg"])

        # In-memory data, loaded from / saved to DATA_FILE
        self.records = []        # list of waste bag records
        self.custody_log = []    # list of custody handoff entries
        self.next_bag_number = 1

        self.load_data()

        self.create_styles()
        self.create_menu()
        self.create_header()
        self.create_tabs()
        self.refresh_all_views()

    # -----------------------------------------------------------
    # Colour theme / ttk styles
    # -----------------------------------------------------------
    def create_styles(self):
        style = ttk.Style(self)
        # "clam" is the theme that allows background colours to actually show
        style.theme_use("clam")

        style.configure("TFrame", background=COLORS["bg"])
        style.configure("Card.TFrame", background=COLORS["card"])

        style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["text"], font=("Segoe UI", 10))
        style.configure("Card.TLabel", background=COLORS["card"], foreground=COLORS["text"], font=("Segoe UI", 10))
        style.configure("Heading.TLabel", background=COLORS["bg"], foreground=COLORS["primary_dark"],
                         font=("Segoe UI", 15, "bold"))
        style.configure("Muted.TLabel", background=COLORS["bg"], foreground=COLORS["muted"], font=("Segoe UI", 9))
        style.configure("Stat.TLabel", background=COLORS["bg"], foreground=COLORS["primary"], font=("Segoe UI", 16, "bold"))

        # Notebook (tabs)
        style.configure("TNotebook", background=COLORS["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", padding=(16, 8), font=("Segoe UI", 10, "bold"),
                         background="#d7ece5", foreground=COLORS["primary_dark"])
        style.map("TNotebook.Tab",
                  background=[("selected", COLORS["primary"])],
                  foreground=[("selected", "white")])

        # Buttons
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"),
                         background=COLORS["primary"], foreground="white", padding=8, borderwidth=0)
        style.map("Primary.TButton",
                  background=[("active", COLORS["primary_dark"])])

        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"),
                         background=COLORS["accent"], foreground="white", padding=8, borderwidth=0)
        style.map("Accent.TButton", background=[("active", "#b45309")])

        style.configure("Danger.TButton", font=("Segoe UI", 10, "bold"),
                         background=COLORS["danger"], foreground="white", padding=8, borderwidth=0)
        style.map("Danger.TButton", background=[("active", "#991b1b")])

        # Treeview (tables)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"),
                         background=COLORS["primary"], foreground="white")
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=26,
                         background="white", fieldbackground="white")
        style.map("Treeview", background=[("selected", COLORS["primary"])],
                  foreground=[("selected", "white")])

        # Entry / Combobox
        style.configure("TEntry", padding=5)
        style.configure("TCombobox", padding=5)

    def create_header(self):
        header = tk.Frame(self, bg=COLORS["primary"], height=64)
        header.pack(fill=tk.X, side=tk.TOP)

        tk.Label(
            header, text="\U0001F3E5  MedWaste Tracker",
            font=("Segoe UI", 18, "bold"), fg="white", bg=COLORS["primary"]
        ).pack(side=tk.LEFT, padx=20, pady=12)

        tk.Label(
            header, text="Biomedical Waste Management System",
            font=("Segoe UI", 10), fg="#d7ece5", bg=COLORS["primary"]
        ).pack(side=tk.LEFT, padx=0, pady=12)

        tk.Label(
            header, text="\u25CF  Running", font=("Segoe UI", 9, "bold"),
            fg=COLORS["primary_dark"], bg="#d1fae5", padx=10, pady=4
        ).pack(side=tk.RIGHT, padx=20, pady=15)

    # -----------------------------------------------------------
    # Data persistence
    # -----------------------------------------------------------
    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    data = json.load(f)
                    self.records = data.get("records", [])
                    self.custody_log = data.get("custody_log", [])
                    self.next_bag_number = data.get("next_bag_number", 1)
            except (json.JSONDecodeError, IOError):
                messagebox.showwarning(
                    "Data File Error",
                    "Could not read existing data file. Starting with empty records."
                )

    def save_data(self):
        data = {
            "records": self.records,
            "custody_log": self.custody_log,
            "next_bag_number": self.next_bag_number,
        }
        try:
            with open(DATA_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except IOError:
            messagebox.showerror("Save Error", "Could not save data to file.")

    # -----------------------------------------------------------
    # Menu bar
    # -----------------------------------------------------------
    def create_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Save Now", command=self.save_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_exit)
        menubar.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menubar)

    def show_about(self):
        messagebox.showinfo(
            "About",
            "MedWaste Tracker\n\n"
            "A mini project for tracking segregation, tagging and\n"
            "custody of biomedical waste in a healthcare facility.\n\n"
            "Built with Python and Tkinter."
        )

    def on_exit(self):
        self.save_data()
        self.destroy()

    # -----------------------------------------------------------
    # Tabs (Notebook)
    # -----------------------------------------------------------
    def create_tabs(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tab_dashboard = ttk.Frame(self.notebook)
        self.tab_add = ttk.Frame(self.notebook)
        self.tab_records = ttk.Frame(self.notebook)
        self.tab_custody = ttk.Frame(self.notebook)
        self.tab_reports = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_dashboard, text="  \U0001F4CA  Dashboard  ")
        self.notebook.add(self.tab_add, text="  \u2795  Add Waste Bag  ")
        self.notebook.add(self.tab_records, text="  \U0001F4CB  Records  ")
        self.notebook.add(self.tab_custody, text="  \U0001F69A  Custody Tracking  ")
        self.notebook.add(self.tab_reports, text="  \U0001F4C8  Reports  ")

        self.build_dashboard_tab()
        self.build_add_tab()
        self.build_records_tab()
        self.build_custody_tab()
        self.build_reports_tab()

    # -----------------------------------------------------------
    # 1. DASHBOARD TAB
    # -----------------------------------------------------------
    def build_dashboard_tab(self):
        frame = self.tab_dashboard

        ttk.Label(frame, text="Dashboard Summary", style="Heading.TLabel").pack(
            anchor="w", padx=15, pady=(15, 10)
        )

        # Four coloured stat cards in a row
        stats_frame = ttk.Frame(frame)
        stats_frame.pack(anchor="w", padx=15, pady=5, fill=tk.X)

        def make_stat_card(parent, title):
            card = tk.Frame(parent, bg=COLORS["card"], highlightthickness=1,
                             highlightbackground="#d1e7e0", padx=18, pady=12)
            card.pack(side=tk.LEFT, padx=(0, 12), fill=tk.BOTH, expand=True)
            tk.Label(card, text=title, font=("Segoe UI", 9), fg=COLORS["muted"], bg=COLORS["card"]).pack(anchor="w")
            value_lbl = tk.Label(card, text="0", font=("Segoe UI", 20, "bold"),
                                  fg=COLORS["primary"], bg=COLORS["card"])
            value_lbl.pack(anchor="w", pady=(4, 0))
            return value_lbl

        self.lbl_total = make_stat_card(stats_frame, "Total Bags")
        self.lbl_pending = make_stat_card(stats_frame, "Pending Disposal")
        self.lbl_disposed = make_stat_card(stats_frame, "Disposed")
        self.lbl_handoffs = make_stat_card(stats_frame, "Custody Handoffs")

        ttk.Button(frame, text="\U0001F504 Refresh", style="Primary.TButton", command=self.refresh_all_views).pack(
            anchor="w", padx=15, pady=12
        )

        ttk.Label(frame, text="Recent Bags", style="Heading.TLabel").pack(
            anchor="w", padx=15, pady=(10, 5)
        )

        columns = ("bag_id", "waste_type", "bin", "status")
        self.dashboard_tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)
        for col, text, width in [
            ("bag_id", "Bag ID", 100),
            ("waste_type", "Waste Type", 150),
            ("bin", "Bin", 120),
            ("status", "Status", 120),
        ]:
            self.dashboard_tree.heading(col, text=text)
            self.dashboard_tree.column(col, width=width)
        self.dashboard_tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

    def update_dashboard(self):
        total = len(self.records)
        disposed = sum(1 for r in self.records if r["status"] == "Disposed")
        pending = total - disposed

        self.lbl_total.config(text=str(total))
        self.lbl_pending.config(text=str(pending))
        self.lbl_disposed.config(text=str(disposed))
        self.lbl_handoffs.config(text=str(len(self.custody_log)))

        for row in self.dashboard_tree.get_children():
            self.dashboard_tree.delete(row)
        for r in reversed(self.records[-10:]):
            self.dashboard_tree.insert(
                "", tk.END, values=(r["bag_id"], r["waste_type"], r["bin"], r["status"])
            )

    # -----------------------------------------------------------
    # 2. ADD WASTE BAG TAB
    # -----------------------------------------------------------
    def build_add_tab(self):
        frame = self.tab_add

        ttk.Label(frame, text="Waste Segregation & Bag Creation", style="Heading.TLabel").pack(
            anchor="w", padx=15, pady=(15, 10)
        )

        card = tk.Frame(frame, bg=COLORS["card"], highlightthickness=1,
                         highlightbackground="#d1e7e0", padx=25, pady=20)
        card.pack(anchor="w", padx=15, fill=tk.X)

        form = tk.Frame(card, bg=COLORS["card"])
        form.pack(anchor="w", fill=tk.X)

        tk.Label(form, text="Waste Type:", bg=COLORS["card"], font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, sticky="w", pady=6
        )
        self.waste_type_var = tk.StringVar()
        self.waste_dropdown = ttk.Combobox(
            form, textvariable=self.waste_type_var,
            values=list(WASTE_TYPES.keys()), state="readonly", width=30
        )
        self.waste_dropdown.grid(row=0, column=1, sticky="w", padx=10, pady=6)
        self.waste_dropdown.bind("<<ComboboxSelected>>", self.on_waste_type_selected)

        tk.Label(form, text="Staff ID:", bg=COLORS["card"], font=("Segoe UI", 10, "bold")).grid(
            row=1, column=0, sticky="w", pady=6
        )
        self.staff_id_entry = ttk.Entry(form, width=32)
        self.staff_id_entry.grid(row=1, column=1, sticky="w", padx=10, pady=6)

        # Result box showing recommended bin - a coloured swatch + text
        self.bin_result_box = tk.Frame(card, bg="#f0faf6", highlightthickness=1,
                                        highlightbackground="#bfe7d8", padx=15, pady=12)
        self.bin_result_box.pack(anchor="w", fill=tk.X, pady=(15, 0))

        self.bin_swatch = tk.Label(self.bin_result_box, text="   ", bg="white", width=3, height=1)
        self.bin_swatch.grid(row=0, column=0, rowspan=2, padx=(0, 12), sticky="n")

        self.bin_result_label = tk.Label(
            self.bin_result_box, text="Select a waste type to see the recommended bin",
            font=("Segoe UI", 12, "bold"), fg=COLORS["primary_dark"], bg="#f0faf6"
        )
        self.bin_result_label.grid(row=0, column=1, sticky="w")

        self.bin_desc_label = tk.Label(self.bin_result_box, text="", wraplength=500,
                                        bg="#f0faf6", fg=COLORS["text"], justify="left")
        self.bin_desc_label.grid(row=1, column=1, sticky="w")

        ttk.Button(
            card, text="\u2795 Create & Save Waste Bag", style="Primary.TButton", command=self.create_bag
        ).pack(anchor="w", pady=(18, 0))

    def on_waste_type_selected(self, event=None):
        waste_type = self.waste_type_var.get()
        if waste_type in WASTE_TYPES:
            bin_name, desc = WASTE_TYPES[waste_type]
            self.bin_result_label.config(text=f"Recommended Bin: {bin_name}")
            self.bin_desc_label.config(text=desc)
            self.bin_swatch.config(bg=BIN_COLOR_MAP.get(bin_name, "white"))

    def create_bag(self):
        waste_type = self.waste_type_var.get()
        staff_id = self.staff_id_entry.get().strip()

        if not waste_type:
            messagebox.showwarning("Missing Info", "Please select a waste type.")
            return
        if not staff_id:
            messagebox.showwarning("Missing Info", "Please enter a Staff ID.")
            return

        bin_name, desc = WASTE_TYPES[waste_type]
        bag_id = f"MW-{1000 + self.next_bag_number}"
        self.next_bag_number += 1

        record = {
            "bag_id": bag_id,
            "waste_type": waste_type,
            "bin": bin_name,
            "staff_id": staff_id,
            "status": "Pending",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.records.append(record)
        self.save_data()
        self.refresh_all_views()

        # Reset form
        self.waste_dropdown.set("")
        self.staff_id_entry.delete(0, tk.END)
        self.bin_result_label.config(text="Select a waste type to see the recommended bin")
        self.bin_desc_label.config(text="")
        self.bin_swatch.config(bg="white")

        messagebox.showinfo("Bag Created", f"Waste bag '{bag_id}' created and saved successfully.")

    # -----------------------------------------------------------
    # 3. RECORDS TAB
    # -----------------------------------------------------------
    def build_records_tab(self):
        frame = self.tab_records

        ttk.Label(frame, text="All Waste Bag Records", style="Heading.TLabel").pack(
            anchor="w", padx=15, pady=(15, 10)
        )

        search_frame = ttk.Frame(frame)
        search_frame.pack(anchor="w", padx=15, pady=5, fill=tk.X)

        ttk.Label(search_frame, text="\U0001F50D Search (Bag ID or Waste Type):").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, width=25)
        self.search_entry.pack(side=tk.LEFT, padx=8)
        ttk.Button(search_frame, text="Search", style="Primary.TButton", command=self.search_records).pack(side=tk.LEFT, padx=4)
        ttk.Button(search_frame, text="Clear", style="Accent.TButton", command=self.refresh_records_tree).pack(side=tk.LEFT, padx=4)

        columns = ("bag_id", "waste_type", "bin", "staff_id", "status", "created_at")
        self.records_tree = ttk.Treeview(frame, columns=columns, show="headings", height=14)
        headers = {
            "bag_id": "Bag ID", "waste_type": "Waste Type", "bin": "Bin",
            "staff_id": "Staff ID", "status": "Status", "created_at": "Created At",
        }
        widths = {"bag_id": 90, "waste_type": 130, "bin": 100, "staff_id": 90, "status": 90, "created_at": 150}
        for col in columns:
            self.records_tree.heading(col, text=headers[col])
            self.records_tree.column(col, width=widths[col])
        self.records_tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(anchor="w", padx=15, pady=(0, 15))
        ttk.Button(btn_frame, text="\u2705 Mark Selected as Disposed", style="Primary.TButton",
                   command=self.mark_disposed).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="\U0001F5D1 Delete Selected Record", style="Danger.TButton",
                   command=self.delete_record).pack(side=tk.LEFT, padx=4)

    def refresh_records_tree(self):
        for row in self.records_tree.get_children():
            self.records_tree.delete(row)
        for r in self.records:
            self.records_tree.insert(
                "", tk.END, iid=r["bag_id"],
                values=(r["bag_id"], r["waste_type"], r["bin"], r["staff_id"], r["status"], r["created_at"])
            )

    def search_records(self):
        query = self.search_entry.get().strip().lower()
        for row in self.records_tree.get_children():
            self.records_tree.delete(row)
        for r in self.records:
            if query in r["bag_id"].lower() or query in r["waste_type"].lower():
                self.records_tree.insert(
                    "", tk.END, iid=r["bag_id"],
                    values=(r["bag_id"], r["waste_type"], r["bin"], r["staff_id"], r["status"], r["created_at"])
                )

    def mark_disposed(self):
        selected = self.records_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a record first.")
            return
        bag_id = selected[0]
        for r in self.records:
            if r["bag_id"] == bag_id:
                r["status"] = "Disposed"
                break
        self.save_data()
        self.refresh_all_views()

    def delete_record(self):
        selected = self.records_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a record first.")
            return
        bag_id = selected[0]
        confirm = messagebox.askyesno("Confirm Delete", f"Delete record '{bag_id}'? This cannot be undone.")
        if confirm:
            self.records = [r for r in self.records if r["bag_id"] != bag_id]
            self.save_data()
            self.refresh_all_views()

    # -----------------------------------------------------------
    # 4. CUSTODY TRACKING TAB
    # -----------------------------------------------------------
    def build_custody_tab(self):
        frame = self.tab_custody

        ttk.Label(frame, text="Custody Handoff Tracking", style="Heading.TLabel").pack(
            anchor="w", padx=15, pady=(15, 10)
        )

        card = tk.Frame(frame, bg=COLORS["card"], highlightthickness=1,
                         highlightbackground="#d1e7e0", padx=20, pady=18)
        card.pack(anchor="w", padx=15, fill=tk.X, pady=(0, 15))

        form = tk.Frame(card, bg=COLORS["card"])
        form.pack(anchor="w", fill=tk.X)

        tk.Label(form, text="Bag ID:", bg=COLORS["card"], font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        self.custody_bag_entry = ttk.Entry(form, width=18)
        self.custody_bag_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(form, text="Staff ID:", bg=COLORS["card"], font=("Segoe UI", 10, "bold")).grid(row=0, column=2, sticky="w", pady=5)
        self.custody_staff_entry = ttk.Entry(form, width=18)
        self.custody_staff_entry.grid(row=0, column=3, padx=10, pady=5)

        tk.Label(form, text="Location:", bg=COLORS["card"], font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        self.custody_location_entry = ttk.Entry(form, width=18)
        self.custody_location_entry.grid(row=1, column=1, padx=10, pady=5)

        ttk.Button(form, text="\U0001F69A Record Handoff", style="Primary.TButton", command=self.record_handoff).grid(
            row=1, column=3, sticky="w", padx=10, pady=5
        )

        columns = ("bag_id", "staff_id", "location", "time")
        self.custody_tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)
        for col, text, width in [
            ("bag_id", "Bag ID", 100),
            ("staff_id", "Staff ID", 100),
            ("location", "Location", 200),
            ("time", "Time", 160),
        ]:
            self.custody_tree.heading(col, text=text)
            self.custody_tree.column(col, width=width)
        self.custody_tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        ttk.Button(
            frame,
            text="\U0001F5D1 Delete Selected Handoff",
            style="Danger.TButton",
            command=self.delete_custody_handoff,
        ).pack(anchor="w", padx=15, pady=(0, 15))

    def record_handoff(self):
        bag_id = self.custody_bag_entry.get().strip()
        staff_id = self.custody_staff_entry.get().strip()
        location = self.custody_location_entry.get().strip()

        if not bag_id or not staff_id or not location:
            messagebox.showwarning("Missing Info", "Please fill in Bag ID, Staff ID and Location.")
            return

        # Basic check: warn (but still allow) if the bag ID does not exist in records
        if not any(r["bag_id"] == bag_id for r in self.records):
            messagebox.showwarning(
                "Unknown Bag ID",
                f"'{bag_id}' was not found in existing records.\nThe handoff will still be logged."
            )

        entry = {
            "bag_id": bag_id,
            "staff_id": staff_id,
            "location": location,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.custody_log.append(entry)
        self.save_data()
        self.refresh_all_views()

        self.custody_bag_entry.delete(0, tk.END)
        self.custody_staff_entry.delete(0, tk.END)
        self.custody_location_entry.delete(0, tk.END)

        messagebox.showinfo("Recorded", "Custody handoff recorded successfully.")

    def refresh_custody_tree(self):
        for row in self.custody_tree.get_children():
            self.custody_tree.delete(row)
        for index in range(len(self.custody_log) - 1, -1, -1):
            entry = self.custody_log[index]
            self.custody_tree.insert(
                "",
                tk.END,
                iid=f"custody-{index}",
                values=(entry["bag_id"], entry["staff_id"], entry["location"], entry["time"]),
            )

    def delete_custody_handoff(self):
        """Delete the selected custody handoff after confirmation."""
        selected = self.custody_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a custody handoff first.")
            return

        try:
            entry_index = int(selected[0].removeprefix("custody-"))
            entry = self.custody_log[entry_index]
        except (ValueError, IndexError):
            messagebox.showerror("Delete Error", "The selected custody handoff could not be found.")
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Delete this custody handoff? This cannot be undone.\n\n"
            f"Bag ID: {entry['bag_id']}\n"
            f"Staff ID: {entry['staff_id']}\n"
            f"Location: {entry['location']}",
        )
        if not confirm:
            return

        self.custody_log.pop(entry_index)
        self.save_data()
        self.refresh_all_views()
        messagebox.showinfo("Deleted", "Custody handoff deleted successfully.")

    # -----------------------------------------------------------
    # 5. REPORTS TAB
    # -----------------------------------------------------------
    def build_reports_tab(self):
        frame = self.tab_reports

        ttk.Label(frame, text="Waste Composition Report", style="Heading.TLabel").pack(
            anchor="w", padx=15, pady=(15, 10)
        )

        columns = ("waste_type", "count", "percentage")
        self.reports_tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)
        for col, text, width in [
            ("waste_type", "Waste Type", 180),
            ("count", "Count", 100),
            ("percentage", "Percentage", 120),
        ]:
            self.reports_tree.heading(col, text=text)
            self.reports_tree.column(col, width=width)
        self.reports_tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        ttk.Button(frame, text="\U0001F4C4 Export Report to CSV", style="Primary.TButton", command=self.export_csv).pack(
            anchor="w", padx=15, pady=10
        )

    def update_reports(self):
        for row in self.reports_tree.get_children():
            self.reports_tree.delete(row)

        total = len(self.records)
        counts = {}
        for r in self.records:
            counts[r["waste_type"]] = counts.get(r["waste_type"], 0) + 1

        for waste_type, count in counts.items():
            pct = (count / total * 100) if total else 0
            self.reports_tree.insert("", tk.END, values=(waste_type, count, f"{pct:.1f}%"))

    def export_csv(self):
        if not self.records:
            messagebox.showinfo("No Data", "There are no records to export.")
            return

        filename = f"waste_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        try:
            with open(filename, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Bag ID", "Waste Type", "Bin", "Staff ID", "Status", "Created At"])
                for r in self.records:
                    writer.writerow(
                        [r["bag_id"], r["waste_type"], r["bin"], r["staff_id"], r["status"], r["created_at"]]
                    )
            messagebox.showinfo("Exported", f"Report exported successfully as '{filename}'.")
        except IOError:
            messagebox.showerror("Export Error", "Could not write the CSV file.")

    # -----------------------------------------------------------
    # Refresh everything at once
    # -----------------------------------------------------------
    def refresh_all_views(self):
        self.update_dashboard()
        self.refresh_records_tree()
        self.refresh_custody_tree()
        self.update_reports()


if __name__ == "__main__":
    app = MedWasteApp()
    app.protocol("WM_DELETE_WINDOW", app.on_exit)
    app.mainloop()
