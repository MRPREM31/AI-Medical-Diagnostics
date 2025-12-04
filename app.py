from flask import Flask, render_template, request, make_response
from dotenv import load_dotenv
load_dotenv("groq.env")

from Utils.Agents import Cardiologist, Psychologist, Pulmonologist, MultidisciplinaryTeam

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import io
import re
from datetime import datetime
import qrcode
import textwrap
import base64


app = Flask(__name__)


# -------------------------------------------------------
# CLEAN + SUMMARIZE DIAGNOSIS (OPTION A)
# -------------------------------------------------------
def clean_and_summarize(text):
    # remove markdown
    cleaned = text.replace("**", "").replace("* ", "• ").replace("*", "").replace("#", "")

    # split into sentences/bullets
    parts = re.split(r"\n|•|-", cleaned)
    parts = [p.strip() for p in parts if len(p.strip()) > 10]

    # take first 6 key points for 1-page PDF
    summary = "• " + "\n• ".join(parts[:6])
    return summary


# -------------------------------------------------------
# BULLET FORMATTER (Fixes your issue)
# -------------------------------------------------------
def format_bullets(text):
    # Force each bullet to a new line
    text = text.replace("•", "\n•")

    # Clean duplicate blank lines
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return "\n".join(lines)


# -------------------------------------------------------
# HOME PAGE
# -------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    diagnosis = None
    qr_base64 = None

    patient = {"name": "Unknown Patient", "age": "N/A", "contact": "N/A"}

    if request.method == "POST":

        uploaded_file = request.files.get("report_file")
        medical_report = ""

        if uploaded_file and uploaded_file.filename.endswith(".txt"):
            medical_report = uploaded_file.read().decode("utf-8")

        if not medical_report:
            medical_report = request.form.get("report", "")

        if not medical_report.strip():
            return render_template("index.html", diagnosis="❌ No report provided", patient=patient)

        # extract patient info
        name_match = re.search(r"Patient Name:\s*(.*)", medical_report)
        age_match = re.search(r"Age:\s*(.*)", medical_report)
        contact_match = re.search(r"Contact:\s*(.*)", medical_report)

        patient["name"] = name_match.group(1).strip() if name_match else "Unknown Patient"
        patient["age"] = age_match.group(1).strip() if age_match else "N/A"
        patient["contact"] = contact_match.group(1).strip() if contact_match else "N/A"

        # run AI agents
        cardio = Cardiologist(medical_report).run()
        psycho = Psychologist(medical_report).run()
        pulmo = Pulmonologist(medical_report).run()

        full_ai_output = MultidisciplinaryTeam(cardio, psycho, pulmo).run()

        # summarize for home + pdf
        diagnosis = clean_and_summarize(full_ai_output)
        diagnosis = format_bullets(diagnosis)

        # Generate QR for home page
        qr_text = f"{patient['name']} | {datetime.now().strftime('%Y-%m-%d')}"
        qr = qrcode.make(qr_text)
        qr_buffer = io.BytesIO()
        qr.save(qr_buffer, format="PNG")
        qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode("utf-8")

    return render_template("index.html", diagnosis=diagnosis, patient=patient, qr=qr_base64)


# -------------------------------------------------------
# PDF GENERATION — One Page Professional
# -------------------------------------------------------
@app.route("/download_pdf", methods=["POST"])
def download_pdf():

    diagnosis = request.form["diagnosis_text"]
    name = request.form.get("patient_name", "Unknown Patient")
    age = request.form.get("patient_age", "N/A")
    contact = request.form.get("patient_contact", "N/A")

    # ensure bullet formatting
    diagnosis = format_bullets(diagnosis)

    filename = f"{name.replace(' ', '_')}_Diagnosis_Report.pdf"

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)


    # --- HOSPITAL LOGO ---
    try:
        logo = ImageReader("static/hospital_logo.png")
        pdf.drawImage(logo, 40, 720, width=90, height=60, mask="auto")
    except:
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(40, 760, "Hospital Logo")


    # --- REPORT TITLE ---
    pdf.setFillColor(colors.HexColor("#0A5CCF"))
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(170, 770, "MEDICAL DIAGNOSTIC REPORT")
    pdf.setFillColor(colors.black)


    # --- PATIENT DETAILS BOX ---
    pdf.setStrokeColor(colors.HexColor("#0A5CCF"))
    pdf.rect(40, 630, 520, 90)

    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(50, 710, "Patient Details")

    pdf.setFont("Helvetica", 11)
    pdf.drawString(60, 690, f"Name     : {name}")
    pdf.drawString(60, 672, f"Age      : {age}")
    pdf.drawString(60, 654, f"Contact  : {contact}")
    pdf.drawString(60, 636, f"Date     : {datetime.now().strftime('%Y-%m-%d')}")


    # --- BLUE HEADER: Diagnosis Summary ---
    pdf.setFillColor(colors.HexColor("#0A5CCF"))
    pdf.rect(40, 610, 520, 22, fill=True, stroke=False)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(50, 616, "Diagnosis Summary")
    pdf.setFillColor(colors.black)


    # --- WRITE DIAGNOSIS WITH BULLETS (NEW LINE FIX) ---
    pdf.setFont("Helvetica", 10)
    y = 590

    lines = diagnosis.split("\n")
    for line in lines:
        wrapped = textwrap.wrap(line, width=110)
        for w in wrapped:
            pdf.drawString(50, y, w)
            y -= 14
            if y < 150:
                break


    # --- QR CODE ---
    qr_data = f"{name} | Verified | {datetime.now().strftime('%Y-%m-%d')}"
    qr_img = qrcode.make(qr_data)
    qr_buf = io.BytesIO()
    qr_img.save(qr_buf, format="PNG")
    qr_buf.seek(0)

    pdf.drawImage(ImageReader(qr_buf), 450, 150, width=90, height=90)
    pdf.setFont("Helvetica-Oblique", 8)
    pdf.drawString(450, 140, "Scan to verify")


    # --- SIGNATURE ---
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, 150, "Doctor's Signature:")

    pdf.line(50, 140, 250, 140)

    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, 125, "Dr. Automated AI System")
    pdf.drawString(50, 112, "Medical AI Diagnostics Department")


    # --- FOOTER ---
    pdf.setFont("Helvetica-Oblique", 8)
    pdf.drawString(50, 60, "This report is auto-generated using AI-based medical analysis.")
    pdf.drawString(180, 45, "Made by QuantumCoders – NIST University")


    pdf.save()
    buffer.seek(0)

    return make_response(
        buffer.getvalue(),
        200,
        {
            "Content-Type": "application/pdf",
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )



# -------------------------------------------------------
# RUN SERVER
# -------------------------------------------------------
if __name__ == "__main__":
    print("🚀 Server running at http://127.0.0.1:5000")
    app.run(debug=True)
