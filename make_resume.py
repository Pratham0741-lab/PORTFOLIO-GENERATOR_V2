from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def draw_junior_resume():
    filename = "Resume_1_Junior.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    
    # --- HEADER ---
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, 750, "Jordan Smith")
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.darkblue)
    c.drawString(50, 730, "Entry-Level Python Developer")
    c.setFillColor(colors.black)
    
    # --- SKILLS (The Target) ---
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 690, "TECHNICAL SKILLS")
    c.line(50, 685, 550, 685)
    c.setFont("Helvetica", 11)
    c.drawString(50, 665, "• Languages: Python, JavaScript, C++")
    c.drawString(50, 650, "• Web: HTML5, CSS3, Flask, Bootstrap")
    c.drawString(50, 635, "• Tools: Git, VS Code, Linux")

    # --- EDUCATION ---
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 600, "EDUCATION")
    c.line(50, 595, 550, 595)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 575, "B.S. Computer Science | State University")
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(450, 575, "Graduated: 2024")

    # --- PROJECTS ---
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 540, "PROJECTS")
    c.line(50, 535, 550, 535)
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 515, "Portfolio Generator App")
    c.setFont("Helvetica", 11)
    c.drawString(60, 500, "- Built a Flask application to auto-generate portfolios.")
    c.drawString(60, 485, "- Integrated Google Gemini API for AI content generation.")
    
    c.save()
    print(f"✅ Created {filename}")

def draw_executive_resume():
    filename = "Resume_2_Executive.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    
    # --- HEADER (Serif Font for Professional Look) ---
    c.setFont("Times-Bold", 26)
    c.drawString(50, 750, "Dr. Elena Rodriguez")
    c.setFont("Times-Roman", 16)
    c.setFillColor(colors.darkgrey)
    c.drawString(50, 730, "Senior Data Scientist & Project Manager")
    c.setFillColor(colors.black)
    
    # --- SUMMARY ---
    c.setFont("Times-Bold", 14)
    c.drawString(50, 690, "PROFESSIONAL SUMMARY")
    c.setFont("Times-Roman", 11)
    text = "Results-oriented leader with 10+ years driving data strategies for Fortune 500 companies."
    c.drawString(50, 670, text)

    # --- EXPERIENCE (Dense Text) ---
    c.setFont("Times-Bold", 14)
    c.drawString(50, 630, "EXPERIENCE")
    c.line(50, 625, 550, 625)
    
    c.setFont("Times-Bold", 12)
    c.drawString(50, 605, "Lead AI Architect | OmniCorp Global")
    c.drawString(450, 605, "2018 - Present")
    c.setFont("Times-Roman", 11)
    c.drawString(50, 590, "• Spearheaded the deployment of Large Language Models (LLMs) across 4 continents.")
    c.drawString(50, 575, "• Managed a cross-functional team of 15 engineers and data analysts.")
    
    # --- SKILLS (Hidden in text block) ---
    c.setFont("Times-Bold", 14)
    c.drawString(50, 530, "CORE COMPETENCIES")
    c.line(50, 525, 550, 525)
    c.setFont("Times-Roman", 11)
    c.drawString(50, 505, "Machine Learning, TensorFlow, PyTorch, Kubernetes, Azure Cloud, Agile Leadership.")
    c.drawString(50, 490, "Strategic Planning, Stakeholder Management, SQL, Big Data Analytics.")

    c.save()
    print(f"✅ Created {filename}")

def draw_creative_resume():
    filename = "Resume_3_Creative.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    
    # --- SIDEBAR (Simulating Columns) ---
    c.setFillColor(colors.lightgrey)
    c.rect(0, 0, 200, 800, fill=1, stroke=0)
    
    # --- LEFT COLUMN (Skills & Contact) ---
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(20, 750, "Marcus")
    c.drawString(20, 730, "Chen")
    
    c.setFont("Helvetica", 12)
    c.drawString(20, 700, "UX/UI Designer")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(20, 600, "SKILLS")
    c.setFont("Helvetica", 11)
    # List skills vertically in sidebar
    skills = ["Figma", "Adobe XD", "Sketch", "React.js", "CSS Grid", "Wireframing"]
    y = 580
    for s in skills:
        c.drawString(20, y, f"• {s}")
        y -= 20
        
    # --- RIGHT COLUMN (Experience) ---
    c.setFont("Helvetica-Bold", 18)
    c.drawString(230, 750, "Work Experience")
    c.line(230, 745, 550, 745)
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(230, 720, "Product Designer | Creative Agency")
    c.setFont("Helvetica", 10)
    c.drawString(230, 705, "Designed accessible user interfaces for fintech startups.")
    c.drawString(230, 690, "Collaborated with developers to implement pixel-perfect designs.")
    
    c.save()
    print(f"✅ Created {filename}")

if __name__ == "__main__":
    draw_junior_resume()
    draw_executive_resume()
    draw_creative_resume()