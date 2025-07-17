import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
import fitz  # PyMuPDF for PDF scanning
from pdf_reader import scan_pdf_and_insert_data

# === Setup SQLite database ===
conn = sqlite3.connect('students.db')
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    roll_number TEXT NOT NULL UNIQUE
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS marks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    subject TEXT,
    marks INTEGER,
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
)
""")
conn.commit()

# === GUI Setup ===
root = tk.Tk()
root.title("Student Record System")
root.geometry("1000x720")
root.resizable(False, False)
root.eval('tk::PlaceWindow . center')

style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", background="black", foreground="#00FF00")
style.configure("TEntry", fieldbackground="black", foreground="#00FF00")
style.configure("TButton", background="black", foreground="#00FF00")
style.configure("Treeview", background="black", foreground="#00FF00", fieldbackground="black")
style.configure("Treeview.Heading", background="black", foreground="#00FF00")
root.configure(bg="black")

# === Form ===
form_frame = tk.Frame(root, bg="black")
form_frame.pack(pady=5)

tk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky="e", padx=10)
entry_name = ttk.Entry(form_frame, width=30)
entry_name.grid(row=0, column=1, padx=5, pady=5)

tk.Label(form_frame, text="Roll No:").grid(row=1, column=0, sticky="e", padx=10)
entry_roll = ttk.Entry(form_frame, width=30)
entry_roll.grid(row=1, column=1, padx=5, pady=5)

subject_frame = tk.Frame(root, bg="black")
subject_frame.pack()
subject_entries = []

def add_subject_row():
    row = len(subject_entries)
    sub = ttk.Entry(subject_frame, width=20)
    mark = ttk.Entry(subject_frame, width=10)
    sub.grid(row=row, column=0, padx=5, pady=3)
    mark.grid(row=row, column=1, padx=5, pady=3)
    subject_entries.append((sub, mark))

add_subject_row()

# === Database Logic ===
selected_student_id = None

def clear_form():
    global selected_student_id
    entry_name.delete(0, tk.END)
    entry_roll.delete(0, tk.END)
    for s, m in subject_entries:
        s.destroy()
        m.destroy()
    subject_entries.clear()
    add_subject_row()
    selected_student_id = None
    save_btn.config(text="✅ Save Student", command=save_student)

def save_student():
    name = entry_name.get().strip()
    roll = entry_roll.get().strip()
    if not name or not roll:
        return
    try:
        cursor.execute("INSERT INTO students (name, roll_number) VALUES (?, ?)", (name, roll))
        student_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        return
    for s, m in subject_entries:
        sub = s.get().strip()
        try:
            mark = int(m.get().strip())
        except:
            mark = None
        if sub and mark is not None:
            cursor.execute("INSERT INTO marks (student_id, subject, marks) VALUES (?, ?, ?)", (student_id, sub, mark))
    conn.commit()
    clear_form()
    load_students()

def update_student():
    global selected_student_id
    if not selected_student_id:
        return
    name = entry_name.get().strip()
    roll = entry_roll.get().strip()
    if not name or not roll:
        return
    cursor.execute("UPDATE students SET name=?, roll_number=? WHERE id=?", (name, roll, selected_student_id))
    cursor.execute("DELETE FROM marks WHERE student_id=?", (selected_student_id,))
    for s, m in subject_entries:
        sub = s.get().strip()
        try:
            mark = int(m.get().strip())
        except:
            mark = None
        if sub and mark is not None:
            cursor.execute("INSERT INTO marks (student_id, subject, marks) VALUES (?, ?, ?)", (selected_student_id, sub, mark))
    conn.commit()
    clear_form()
    load_students()

# === PDF Import ===
def scan_pdf_and_insert():
    pdf_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if not pdf_path:
        return

    try:
        name, roll, marks_data = scan_pdf_and_insert_data(pdf_path)

        # Populate the form with extracted data
        entry_name.delete(0, tk.END)
        entry_name.insert(0, name)
        entry_roll.delete(0, tk.END)
        entry_roll.insert(0, roll)

        # Clear existing subject fields
        for s, m in subject_entries:
            s.destroy()
            m.destroy()
        subject_entries.clear()

        # Add extracted subjects
        for subject, mark in marks_data:
            s = ttk.Entry(subject_frame, width=20)
            m = ttk.Entry(subject_frame, width=10)
            s.insert(0, subject)
            m.insert(0, str(mark))
            s.grid()
            m.grid()
            subject_entries.append((s, m))

        save_btn.config(text="✅ Save Student", command=save_student)
        messagebox.showinfo("Success", "PDF scanned and data populated!")

    except Exception as e:
        messagebox.showerror("Scan Failed", str(e))

# === Buttons ===
button_frame = tk.Frame(root, bg="black")
button_frame.pack(pady=5)
ttk.Button(button_frame, text="➕ Add Subject", command=add_subject_row).grid(row=0, column=0, padx=10)
save_btn = ttk.Button(button_frame, text="✅ Save Student", command=save_student)
save_btn.grid(row=0, column=1, padx=10)
ttk.Button(button_frame, text="📄 Scan PDF", command=scan_pdf_and_insert).grid(row=0, column=2, padx=10)

# === Search ===
search_frame = tk.Frame(root, bg="black")
search_frame.pack(pady=5)
search_type = tk.StringVar(value="name")
ttk.Combobox(search_frame, textvariable=search_type, values=["name", "roll"], width=10, state="readonly").grid(row=0, column=0, padx=5)
search_var = tk.StringVar()
search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
search_entry.grid(row=0, column=1, padx=5)

def search_student():
    value = search_var.get().strip()
    field = search_type.get()
    for row in tree.get_children():
        tree.delete(row)
    if field == "name":
        cursor.execute("SELECT id, name, roll_number FROM students WHERE name LIKE ?", (f"%{value}%",))
    else:
        cursor.execute("SELECT id, name, roll_number FROM students WHERE roll_number LIKE ?", (f"%{value}%",))
    for sid, name, roll in cursor.fetchall():
        cursor.execute("SELECT subject, marks FROM marks WHERE student_id=?", (sid,))
        marks = ", ".join(f"{s}: {m}" for s, m in cursor.fetchall())
        tree.insert("", "end", iid=sid, values=(name, roll, marks))

ttk.Button(search_frame, text="🔍 Search", command=search_student).grid(row=0, column=2, padx=5)

# === Table ===
table_frame = tk.Frame(root, bg="black")
table_frame.pack()
columns = ("Name", "Roll", "Subjects")
tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=300 if col == "Subjects" else 120)
tree.pack(side="left", fill="both", expand=True)
ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview).pack(side="right", fill="y")
tree.configure(yscrollcommand=tree.yview)

def load_students():
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute("SELECT id, name, roll_number FROM students")
    for sid, name, roll in cursor.fetchall():
        cursor.execute("SELECT subject, marks FROM marks WHERE student_id=?", (sid,))
        marks = ", ".join(f"{s}: {m}" for s, m in cursor.fetchall())
        tree.insert("", "end", iid=sid, values=(name, roll, marks))

# === Edit/Delete ===
def edit_selected():
    global selected_student_id
    selected = tree.focus()
    if not selected:
        return
    selected_student_id = int(selected)
    cursor.execute("SELECT name, roll_number FROM students WHERE id=?", (selected_student_id,))
    name, roll = cursor.fetchone()
    entry_name.delete(0, tk.END)
    entry_name.insert(0, name)
    entry_roll.delete(0, tk.END)
    entry_roll.insert(0, roll)
    for s, m in subject_entries:
        s.destroy()
        m.destroy()
    subject_entries.clear()
    cursor.execute("SELECT subject, marks FROM marks WHERE student_id=?", (selected_student_id,))
    for sub, mark in cursor.fetchall():
        s = ttk.Entry(subject_frame, width=20)
        m = ttk.Entry(subject_frame, width=10)
        s.insert(0, sub)
        m.insert(0, str(mark))
        s.grid()
        m.grid()
        subject_entries.append((s, m))
    save_btn.config(text="💾 Update Student", command=update_student)

def delete_selected():
    selected = tree.focus()
    if not selected:
        return
    cursor.execute("DELETE FROM students WHERE id=?", (selected,))
    conn.commit()
    clear_form()
    load_students()

action_frame = tk.Frame(root, bg="black")
action_frame.pack(pady=10)
ttk.Button(action_frame, text="✏️ Edit Student", command=edit_selected).grid(row=0, column=0, padx=20)
ttk.Button(action_frame, text="🗑️ Delete Student", command=delete_selected).grid(row=0, column=1, padx=20)

# === Footer ===
footer_frame = tk.Frame(root, bg="black")
footer_frame.pack(fill="both", expand=True, padx=10)
ascii_text = """
 ____  _             _              _             _             
|  _ \\| |_   _  __ _(_)_ __ ___    | |_ ___   ___| | _____ _ __ 
| |_) | | | | |/ _` | | '_ ` _ \\   | __/ _ \\ / __| |/ / _ \\ '__|
|  __/| | |_| | (_| | | | | | | |  | || (_) | (__|   <  __/ |   
|_|   |_|\\__,_|\\__, |_|_| |_| |_|   \\__\\___/ \\___|_|\\_\\___|_|   
               |___/                                                          
Created with ❤️ by Usman 
"""
scrollbar_footer = tk.Scrollbar(footer_frame)
scrollbar_footer.pack(side="right", fill="y")
text = tk.Text(footer_frame, wrap="word", yscrollcommand=scrollbar_footer.set,
               height=6, font=("Courier New", 9), bg="black", fg="#00FF00", bd=0)
text.insert(tk.END, ascii_text)
text.config(state="disabled")
text.pack(fill="both", expand=True)
scrollbar_footer.config(command=text.yview)

# === Run ===
load_students()
root.mainloop()
