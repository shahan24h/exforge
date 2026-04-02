import os
import sys
import json
import anthropic
from datetime import datetime
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_connection, update_lead_status

# ── CONFIG ──────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
REPORTS_DIR       = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "reports"
)
AGENCY_NAME    = "PixelForge"
AGENCY_WEBSITE = "pixelforge.com"
AGENCY_EMAIL   = "shahan@pixelforge.com"
# ────────────────────────────────────────────────────────


def get_audited_leads():
    """Get all audited leads from the database."""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, category, address, phone, website,
               rating, reviews, audit_data, screenshot_path
        FROM leads WHERE status = 'audited'
    """)
    rows = cursor.fetchall()
    conn.close()

    leads = []
    for row in rows:
        audit_data = {}
        try:
            audit_data = json.loads(row[8]) if row[8] else {}
        except:
            pass

        leads.append({
            "id":              row[0],
            "name":            row[1],
            "category":        row[2],
            "address":         row[3],
            "phone":           row[4],
            "website":         row[5],
            "rating":          row[6],
            "reviews":         row[7],
            "audit":           audit_data,
            "screenshot_path": row[9],
        })
    return leads


def get_score_grade(score: int) -> tuple[str, colors.Color]:
    """Convert numeric score to letter grade and color."""
    if score >= 90:
        return "A", colors.HexColor("#27AE60")
    elif score >= 75:
        return "B", colors.HexColor("#F39C12")
    elif score >= 60:
        return "C", colors.HexColor("#E67E22")
    elif score >= 40:
        return "D", colors.HexColor("#E74C3C")
    else:
        return "F", colors.HexColor("#C0392B")


def generate_ai_summary(lead: dict, client: anthropic.Anthropic) -> str:
    """Use Claude to generate a personalized report summary."""
    audit  = lead["audit"]
    issues = audit.get("issues", [])
    score  = audit.get("score", 0)

    prompt = f"""
You are writing a professional website audit report for {lead['name']}, a {lead['category']} in {lead['address']}.

Website: {lead['website']}
SEO Score: {score}/100
Issues found: {', '.join(issues) if issues else 'None'}
Rating: {lead['rating']} stars ({lead['reviews']} reviews)

Write a SHORT 3-sentence personalized summary for this business owner explaining:
1. What we found about their website
2. How these issues are costing them customers
3. How PixelForge can help

Be specific, friendly, and professional. Do not use generic language.
Keep it under 100 words.
"""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text.strip()


def generate_revenue_impact(score: int, reviews: str) -> str:
    """Generate a revenue impact estimate based on score."""
    try:
        review_count = int(reviews)
    except:
        review_count = 50

    if score < 60:
        lost_pct  = "40-60%"
        est_leads = review_count // 3
    elif score < 80:
        lost_pct  = "20-40%"
        est_leads = review_count // 5
    else:
        lost_pct  = "10-20%"
        est_leads = review_count // 10

    return f"Websites with your current score lose approximately {lost_pct} of potential visitors before they make contact. Based on your {reviews} reviews, we estimate you may be missing {est_leads}+ potential customers per month."


def create_pdf_report(lead: dict, summary: str) -> str:
    """Generate a PDF report for a single lead."""
    os.makedirs(REPORTS_DIR, exist_ok=True)

    safe_name = lead["name"].replace(" ", "_").replace("/", "_")[:30]
    filename  = os.path.join(REPORTS_DIR, f"{safe_name}_report.pdf")

    doc    = SimpleDocTemplate(filename, pagesize=letter,
                               rightMargin=0.75*inch, leftMargin=0.75*inch,
                               topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    story  = []

    # ── Header ──
    header_style = ParagraphStyle(
        "header", fontSize=22, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#2C3E50"), alignment=TA_CENTER
    )
    sub_style = ParagraphStyle(
        "sub", fontSize=11, fontName="Helvetica",
        textColor=colors.HexColor("#7F8C8D"), alignment=TA_CENTER
    )
    story.append(Paragraph("Website Audit Report", header_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(f"Prepared by {AGENCY_NAME} — {AGENCY_WEBSITE}", sub_style))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", sub_style))
    story.append(Spacer(1, 0.3*inch))

    # ── Business Info ──
    section_style = ParagraphStyle(
        "section", fontSize=14, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#2C3E50"), spaceAfter=8
    )
    body_style = ParagraphStyle(
        "body", fontSize=10, fontName="Helvetica",
        textColor=colors.HexColor("#2C3E50"), spaceAfter=4
    )

    story.append(Paragraph("Business Overview", section_style))
    info_data = [
        ["Business Name", lead["name"]],
        ["Category",      lead["category"]],
        ["Address",       lead["address"]],
        ["Phone",         lead["phone"]],
        ["Website",       lead["website"]],
        ["Google Rating", f"{lead['rating']} ⭐ ({lead['reviews']} reviews)"],
    ]
    info_table = Table(info_data, colWidths=[1.5*inch, 5.5*inch])
    info_table.setStyle(TableStyle([
        ("FONTNAME",        (0, 0), (-1, -1), "Helvetica"),
        ("FONTNAME",        (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE",        (0, 0), (-1, -1), 10),
        ("TEXTCOLOR",       (0, 0), (0, -1), colors.HexColor("#7F8C8D")),
        ("TEXTCOLOR",       (1, 0), (1, -1), colors.HexColor("#2C3E50")),
        ("ROWBACKGROUNDS",  (0, 0), (-1, -1), [colors.HexColor("#F8F9FA"), colors.white]),
        ("GRID",            (0, 0), (-1, -1), 0.5, colors.HexColor("#DEE2E6")),
        ("PADDING",         (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.3*inch))

    # ── Score Card ──
    audit  = lead["audit"]
    score  = audit.get("score", 0)
    grade, grade_color = get_score_grade(score)

    story.append(Paragraph("Website Score", section_style))
    score_data = [
        ["Overall Score", f"{score}/100", "Grade", grade],
        ["HTTPS",         "✓" if audit.get("seo", {}).get("https") else "✗",
         "Mobile Ready",  "✓" if audit.get("seo", {}).get("mobile_viewport") else "✗"],
        ["Title Tag",     "✓" if audit.get("seo", {}).get("title") else "✗",
         "Meta Desc",     "✓" if audit.get("seo", {}).get("meta_description") else "✗"],
    ]
    score_table = Table(score_data, colWidths=[1.8*inch, 1.7*inch, 1.8*inch, 1.7*inch])
    score_table.setStyle(TableStyle([
        ("FONTNAME",    (0, 0), (-1, -1), "Helvetica"),
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 11),
        ("TEXTCOLOR",   (1, 0), (1, 0), colors.HexColor("#E74C3C") if score < 60 else colors.HexColor("#27AE60")),
        ("TEXTCOLOR",   (3, 0), (3, 0), grade_color),
        ("BACKGROUND",  (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
        ("TEXTCOLOR",   (0, 0), (-1, 0), colors.white),
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#DEE2E6")),
        ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
        ("PADDING",     (0, 0), (-1, -1), 10),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 0.3*inch))

    # ── Issues Found ──
    issues = audit.get("issues", [])
    if issues:
        story.append(Paragraph("Issues Found", section_style))
        for issue in issues:
            story.append(Paragraph(f"• {issue}", body_style))
        story.append(Spacer(1, 0.2*inch))

    # ── Revenue Impact ──
    story.append(Paragraph("Revenue Impact Estimate", section_style))
    impact = generate_revenue_impact(score, lead["reviews"])
    impact_style = ParagraphStyle(
        "impact", fontSize=10, fontName="Helvetica",
        textColor=colors.HexColor("#2C3E50"),
        backColor=colors.HexColor("#FFF3CD"),
        borderPad=10, spaceAfter=10
    )
    story.append(Paragraph(impact, impact_style))
    story.append(Spacer(1, 0.2*inch))

    # ── AI Summary ──
    story.append(Paragraph("Our Analysis", section_style))
    story.append(Paragraph(summary, body_style))
    story.append(Spacer(1, 0.3*inch))

    # ── Screenshot ──
    screenshot = lead.get("screenshot_path")
    if screenshot and os.path.exists(screenshot):
        story.append(Paragraph("Current Website Screenshot", section_style))
        story.append(Spacer(1, 0.1*inch))
        img = Image(screenshot, width=6.5*inch, height=3.5*inch)
        story.append(img)
        story.append(Spacer(1, 0.3*inch))

    # ── Footer ──
    footer_style = ParagraphStyle(
        "footer", fontSize=9, fontName="Helvetica",
        textColor=colors.HexColor("#7F8C8D"), alignment=TA_CENTER
    )
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(
        f"This report was prepared by {AGENCY_NAME} | {AGENCY_EMAIL} | {AGENCY_WEBSITE}",
        footer_style
    ))
    story.append(Paragraph(
        "We specialize in helping local businesses improve their online presence.",
        footer_style
    ))

    doc.build(story)
    return filename


def run_report_generator():
    """Main report generation pipeline."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    leads  = get_audited_leads()

    if not leads:
        print("[!] No audited leads to generate reports for.")
        return

    print(f"[+] Generating reports for {len(leads)} audited leads...\n")

    for i, lead in enumerate(leads, 1):
        name = lead["name"]
        print(f"  [{i}/{len(leads)}] Generating report: {name}")

        # Generate AI summary
        try:
            summary = generate_ai_summary(lead, client)
            print(f"    [✓] AI summary generated")
        except Exception as e:
            summary = f"Our audit found several areas where {name}'s website could be improved to attract more customers."
            print(f"    [!] AI summary fallback: {e}")

        # Generate PDF
        try:
            pdf_path = create_pdf_report(lead, summary)
            print(f"    [✓] Report saved: {pdf_path}")

            # Update status
            update_lead_status(lead["phone"], "report_ready")

        except Exception as e:
            print(f"    [✗] Report failed: {e}")

    print(f"\n[DONE] Reports saved to: {REPORTS_DIR}")


if __name__ == "__main__":
    run_report_generator()