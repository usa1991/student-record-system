# 🎓 Student Record System (Retro GUI Version)

A Python-based Student Record Management System using Tkinter and SQLite, now with optional PDF scanning via OCR! It features a classic **green-on-black retro terminal aesthetic**, built for both functionality and fun.

---

## ✨ Features

- ➕ Add students with **name**, **roll number**, and **subject-wise marks**
- 📄 **Scan PDF mark sheets** and auto-fill fields (works with both text-based and scanned PDFs)
- 🔍 Search students by **name** or **roll number**
- ✏️ Edit student details and marks
- 🗑️ Delete students
- ➕ Dynamically add/remove multiple subjects
- 📁 Persistent storage using **SQLite**
- 🖥️ GUI built using **Tkinter**
- 🎨 Inspired by **retro terminal-style** (green-on-black)
- 🪄 No need to install Python (Windows `.exe` included – see `releases/`)
- ✅ Smart fallback to OCR using **Tesseract** if PDF text can't be extracted
- ⚙️ Clean modular structure (`student_gui.py`, `pdf_reader.py`, `student_db.py`)

---

## 📸 Screenshot

> ![Student Record System Screenshot](screenshots/retro-ui.png)

---

## 🧑‍💻 How to Use (from Source)

### 1. Clone the Repository:

```bash
git clone https://github.com/usa1991/student-record-system.git
cd student-record-system
