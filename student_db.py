# student_db_subjects.py
import sqlite3
from colorama import Fore, Style, init


init(autoreset=True)


conn = sqlite3.connect("students.db")
conn.execute("PRAGMA foreign_keys = ON")   # crucial!
cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    roll_number TEXT    NOT NULL UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS marks (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    subject    TEXT,
    marks      INTEGER,
    FOREIGN KEY (student_id)
        REFERENCES students(id)
        ON DELETE CASCADE
)
""")
conn.commit()


def add_student() -> None:
    """Add a student and as many subject‑wise marks as desired."""
    name = input("Enter student name: ").strip()
    roll = input("Enter roll number: ").strip()

    try:
        cursor.execute("INSERT INTO students (name, roll_number) VALUES (?, ?)",
                       (name, roll))
        student_id = cursor.lastrowid

        while True:
            subject = input("Enter subject name (or 'done' to finish): ").strip()
            if subject.lower() == 'done':
                break
            try:
                mark = int(input(f"Enter marks for {subject}: ").strip())
            except ValueError:
                print(Fore.RED + "❌  Marks must be an integer. Try again.")
                continue
            cursor.execute(
                "INSERT INTO marks (student_id, subject, marks) VALUES (?, ?, ?)",
                (student_id, subject, mark)
            )

        conn.commit()
        print(Fore.GREEN + "✅  Student and marks saved.\n")

    except sqlite3.IntegrityError:
        print(Fore.RED + "❌  Roll number already exists. Aborted.\n")

def view_students() -> None:
    """Display each student and their subject‑wise marks."""
    cursor.execute("SELECT * FROM students ORDER BY name COLLATE NOCASE")
    students = cursor.fetchall()

    if not students:
        print(Fore.YELLOW + "⚠️  No students in database.\n")
        return

    print(Fore.CYAN + "\n========== Student Records ==========")
    for stu in students:
        stu_id, name, roll = stu
        print(f"\n🧑  {Fore.LIGHTWHITE_EX}Name:{Style.RESET_ALL} {name} "
              f"| {Fore.LIGHTWHITE_EX}Roll:{Style.RESET_ALL} {roll}")
        cursor.execute(
            "SELECT subject, marks FROM marks WHERE student_id = ?",
            (stu_id,))
        rows = cursor.fetchall()
        if rows:
            for subject, mark in rows:
                print(f"   📚 {subject}: {mark}")
        else:
            print("   ❌  No marks recorded.")
    print()

def search_student() -> None:
    """Search by name *or* roll substring (case‑insensitive)."""
    key = input("Enter name or roll number to search: ").strip()
    like = f"%{key}%"
    cursor.execute("""
        SELECT * FROM students
        WHERE name LIKE ? OR roll_number LIKE ?""", (like, like))
    hits = cursor.fetchall()

    if not hits:
        print(Fore.YELLOW + "🔍  No matching student found.\n")
        return

    print(Fore.CYAN + "\n========== Search Results ==========")
    for stu in hits:
        stu_id, name, roll = stu
        print(f"\n🧑  {name} | Roll {roll}")
        cursor.execute("SELECT subject, marks FROM marks WHERE student_id = ?",
                       (stu_id,))
        for subject, mark in cursor.fetchall():
            print(f"   📚 {subject}: {mark}")
    print()

def delete_student() -> None:
    """Remove a student entirely (cascade deletes their marks)."""
    roll = input("Enter roll number to delete: ").strip()
    cursor.execute("SELECT id FROM students WHERE roll_number = ?", (roll,))
    row = cursor.fetchone()

    if row is None:
        print(Fore.RED + "❌  Student not found.\n")
        return

    confirm = input(f"Are you sure you want to delete roll {roll}? (y/n): ")
    if confirm.lower() != 'y':
        print("❎  Deletion cancelled.\n")
        return

    cursor.execute("DELETE FROM students WHERE id = ?", (row[0],))
    conn.commit()
    print(Fore.GREEN + "🗑️  Student and all marks deleted.\n")

# ----------------------------------------
# Main interactive menu
# ----------------------------------------
def menu() -> None:
    while True:
        print(Fore.LIGHTMAGENTA_EX + "\n====== Student Record System ======")
        print("1. Add Student (with subjects)")
        print("2. View All Students")
        print("3. Search Student")
        print("4. Delete Student")
        print("5. Exit")
        choice = input("Enter your choice (1‑5): ").strip()

        if choice == '1':
            add_student()
        elif choice == '2':
            view_students()
        elif choice == '3':
            search_student()
        elif choice == '4':
            delete_student()
        elif choice == '5':
            print(Fore.GREEN + "👋  Goodbye!")
            break
        else:
            print(Fore.RED + "❌  Invalid choice. Try again.\n")

# ----------------------------------------
# Script entry‑point
# ----------------------------------------
if __name__ == "__main__":
    try:
        menu()
    finally:
        conn.close()
