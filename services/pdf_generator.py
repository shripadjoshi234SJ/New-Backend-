from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


async def generate_summary_pdf(title: str, summary: str, keywords: list, mcqs: list) -> BytesIO:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    pdf.setTitle(title)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(40, height - 40, title)

    pdf.setFont("Helvetica", 11)
    text = pdf.beginText(40, height - 80)
    text.textLines(summary)
    pdf.drawText(text)

    y = height - 140
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(40, y, "Keywords")
    pdf.setFont("Helvetica", 10)
    y -= 20
    for keyword in keywords[:8]:
        pdf.drawString(40, y, f"- {keyword}")
        y -= 15

    y -= 20
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(40, y, "MCQs")
    pdf.setFont("Helvetica", 10)
    y -= 15
    for idx, mcq in enumerate(mcqs[:3], start=1):
        pdf.drawString(40, y, f"{idx}. {mcq.get('question', '')}")
        y -= 12
        for option in mcq.get("options", [])[:4]:
            pdf.drawString(55, y, f"- {option}")
            y -= 10
        y -= 8

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer
