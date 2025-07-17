import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import re

# Tesseract Path (adjust if needed)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def scan_pdf_and_insert_data(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        full_text = ""

        for page_number in range(len(doc)):
            page = doc.load_page(page_number)
            text = page.get_text()
            if text and len(text.strip()) > 30:
                full_text += text + "\n"
            else:
                print(f"⚠️ Text extraction failed on page {page_number}. Trying OCR...")
                pix = page.get_pixmap(dpi=300)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                ocr_text = pytesseract.image_to_string(img)
                print("👉 OCR Result (first 200 chars):\n", ocr_text[:200])
                full_text += ocr_text + "\n"

        doc.close()

        print("\n===== FULL EXTRACTED TEXT =====\n")
        print(full_text)
        print("\n===== END OF EXTRACTED TEXT =====\n")

        name = ""
        roll = ""
        subjects = []

        # === Try Simple PDF format first ===
        simple_name = re.search(r"Name\s*:\s*(.+)", full_text)
        simple_roll = re.search(r"Roll\s*(Number|No\.?)\s*:\s*(\S+)", full_text)

        if simple_name:
            name = simple_name.group(1).strip()
        if simple_roll:
            roll = simple_roll.group(2).strip()

        if "Subjects and Marks" in full_text:
            for line in full_text.splitlines():
                line = line.strip()
                if ":" in line:
                    parts = line.split(":")
                    if len(parts) == 2:
                        subject = parts[0].strip()
                        try:
                            mark = int(parts[1].strip())
                            subjects.append((subject, mark))
                        except:
                            continue

        # === Fallback: Try University Format ===
        if not name or not roll or not subjects:
            uni_name = re.search(r"Student Name\s*:\s*(.+)", full_text)
            uni_roll = re.search(r"Reg\.? No\.?\s*:\s*(\S+)", full_text)

            if uni_name:
                name = uni_name.group(1).strip()
            if uni_roll:
                roll = uni_roll.group(1).strip()

            after_result = False
            for line in full_text.splitlines():
                line = line.strip()
                if "result sheet" in line.lower():
                    after_result = True
                    continue
                if not after_result:
                    continue
                if re.search(r"[A-Za-z].*\d+$", line):
                    try:
                        parts = line.rsplit(" ", 1)
                        subject = parts[0].strip()
                        mark = int(parts[1].strip())
                        subjects.append((subject, mark))
                    except:
                        continue

        # Final check
        if not name or not roll or not subjects:
            raise ValueError("❌ Couldn't extract name, roll number, or subject marks properly.")

        return name, roll, subjects

    except Exception as e:
        raise ValueError("❌ OCR-based parsing failed. Could not extract data.\n\n" + str(e))
