from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.pagesizes import A4
from io import BytesIO

def generate_pdf(symbol, score, decision, entry, stop, target):

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)

    content = []

    content.append(Paragraph(f"Stock: {symbol}", None))
    content.append(Paragraph(f"Score: {score}", None))
    content.append(Paragraph(f"Decision: {decision}", None))
    content.append(Paragraph(f"Entry: {entry:.2f}", None))
    content.append(Paragraph(f"Stop: {stop:.2f}", None))
    content.append(Paragraph(f"Target: {target:.2f}", None))

    doc.build(content)

    buffer.seek(0)
    return buffer
