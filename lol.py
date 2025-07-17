from fpdf import FPDF

# Create a clean and simple marksheet
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

# Student details
pdf.cell(200, 10, txt="Name: Usman Ghani", ln=True)
pdf.cell(200, 10, txt="Roll Number: 101", ln=True)
pdf.cell(200, 10, txt="Subjects and Marks:", ln=True)

# Subject and marks
subjects = {
    "Math": 89,
    "Physics": 78,
    "Chemistry": 85,
    "Biology": 92,
    "English": 88
}

for subject, mark in subjects.items():
    pdf.cell(200, 10, txt=f"{subject}: {mark}", ln=True)

# Save the PDF
pdf.output("clean_marksheet_usman.pdf")
