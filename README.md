# Personal Expense Tracker - College Mini Project

A complete, full-stack Personal Expense Tracker application built with **Python**, **Flask**, **HTML5**, **CSS3**, and **JavaScript**, with persistent data storage in **CSV** format.

---

## 🚀 Key Features

- **Full-Stack Web Architecture**: Powered by a Python Flask REST API backend connected directly to `expenses.csv`.
- **Interactive Visualizations**: Dynamic Doughnut & Bar charts powered by **Chart.js** displaying real-time category distribution and monthly spending trends.
- **Budget Monitor & Alert**: Set a monthly spending threshold with a visual progress bar (alerts in yellow/red when approaching or exceeding budget).
- **Search, Filter & Sort**: Filter transactions by category, search descriptions live, or sort by amount/date.
- **Dark / Light Mode**: Easily toggle between dark and light themes with preference saved in localStorage.
- **One-Click Export**: Export and download expenses directly to CSV format.
- **Dual Mode (Online + Offline)**: Runs connected to the Flask backend or standalone directly in any browser (via localStorage fallback).
- **Bonus Desktop GUI**: Includes a modernized Python Tkinter desktop application (`tracker.py`) sharing the exact same `expenses.csv` database.

---

## 🛠️ Technology Stack

| Layer | Technologies Used |
|---|---|
| **Frontend** | HTML5, CSS3 (Custom Properties, Flexbox, Grid), JavaScript (ES6+), Chart.js |
| **Backend** | Python 3, Flask |
| **Data Storage** | CSV (`expenses.csv`) |
| **Desktop GUI** | Python Tkinter & `ttk` themed widgets |

---

## 📁 Project Structure

```text
expance tracker/
├── app.py              # Flask Web Server & REST API endpoints
├── index.html          # Web UI Dashboard & Form
├── style.css           # Modern CSS styling (Themes, Badges, Animations)
├── script.js           # JavaScript logic, Chart.js graphs, Budget Monitor
├── tracker.py          # Modern Tkinter desktop application
├── expenses.csv        # Shared CSV dataset
└── README.md           # Documentation & Project Guide
```

---

## 💻 How to Run the Project

### Option 1: Run Web Application (Python + Flask + HTML/CSS/JS)
1. Open PowerShell or Command Prompt in this folder:
   ```bash
   cd "c:\Users\Asus\Desktop\expance tracker"
   ```
2. Start the Flask application:
   ```bash
   python app.py
   ```
3. Open your browser and navigate to:
   ```text
   http://127.0.0.1:5000
   ```

### Option 2: Run Without Server (Direct Browser Mode)
- Simply double-click `index.html` in File Explorer. It opens instantly in Chrome/Edge with full functionality (data stored in browser storage).

### Option 3: Run Desktop Tkinter GUI
- Run the following in terminal:
  ```bash
  python tracker.py
  ```

---

## 🎓 Viva / Presentation Questions & Answers

**Q1: Can Tkinter run HTML, CSS, or JavaScript directly?**  
> *Answer:* No. Tkinter is Python's native desktop GUI binding for the Tk toolkit and renders desktop OS widgets. CSS and JavaScript are web browser technologies. To incorporate CSS and JavaScript, we build a Web application using a Python backend (like Flask) with HTML5/CSS3/JavaScript on the frontend.

**Q2: How does data persist across sessions?**  
> *Answer:* Expenses are saved to `expenses.csv` using Python's standard `csv` library. The Flask API reads and writes to this file, ensuring persistence even if the server restarts.

**Q3: How are the charts generated?**  
> *Answer:* We use the Chart.js JavaScript library. It receives aggregated category and monthly totals calculated dynamically from the transaction records and renders responsive canvas graphs.
