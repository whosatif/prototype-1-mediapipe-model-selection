import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
import datetime

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=80, bottom=80, left=120, right=120):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}>'
                      f'<w:top w:w="{top}" w:type="dxa"/>'
                      f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
                      f'<w:left w:w="{left}" w:type="dxa"/>'
                      f'<w:right w:w="{right}" w:type="dxa"/>'
                      f'</w:tcMar>')
    tcPr.append(tcMar)

def add_card(doc, title, items, border_color="0A66C2", bg_color="F4F8FC"):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    cell = table.cell(0, 0)
    cell.width = Inches(6.8)
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=90, bottom=90, left=140, right=140)
    
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}>'
                          f'<w:top w:val="none"/>'
                          f'<w:left w:val="single" w:sz="20" w:space="0" w:color="{border_color}"/>'
                          f'<w:bottom w:val="none"/>'
                          f'<w:right w:val="none"/>'
                          f'</w:tcBorders>')
    tcPr.append(tcBorders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    run_t = p.add_run(title)
    run_t.bold = True
    run_t.font.name = 'Calibri'
    run_t.font.size = Pt(10.5)
    run_t.font.color.rgb = RGBColor(0x0F, 0x29, 0x4A)
    
    for item in items:
        p_item = cell.add_paragraph()
        p_item.paragraph_format.space_before = Pt(1)
        p_item.paragraph_format.space_after = Pt(2)
        p_item.paragraph_format.line_spacing = 1.15
        
        prefix = item.get('prefix', '')
        text = item.get('text', '')
        color = item.get('color', RGBColor(0x22, 0x22, 0x22))
        
        if prefix:
            r_pre = p_item.add_run(prefix)
            r_pre.bold = True
            r_pre.font.name = 'Calibri'
            r_pre.font.size = Pt(9.5)
            r_pre.font.color.rgb = color
            
        r_txt = p_item.add_run(text)
        r_txt.font.name = 'Calibri'
        r_txt.font.size = Pt(9.5)
        r_txt.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
        
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

def generate_quick_doc():
    doc = Document()
    base_dir = r"c:\Users\ATIF\Desktop\fyp project\prototype 1"

    # Compact & tidy page margins (0.6 in)
    for s in doc.sections:
        s.top_margin = Inches(0.55)
        s.bottom_margin = Inches(0.55)
        s.left_margin = Inches(0.65)
        s.right_margin = Inches(0.65)

    PRIMARY = RGBColor(0x0F, 0x29, 0x4A)      # Dark Navy
    SECONDARY = RGBColor(0x0A, 0x66, 0xC2)    # Electric Blue
    ACCENT = RGBColor(0xD9, 0x38, 0x1E)       # Red-Orange
    GREEN = RGBColor(0x27, 0xAE, 0x60)        # Green
    DARK_TEXT = RGBColor(0x22, 0x22, 0x22)
    MUTED = RGBColor(0x66, 0x66, 0x66)

    # Base styling
    normal = doc.styles['Normal']
    normal.font.name = 'Calibri'
    normal.font.size = Pt(10)
    normal.font.color.rgb = DARK_TEXT
    normal.paragraph_format.line_spacing = 1.15
    normal.paragraph_format.space_after = Pt(4)

    # ========================================================
    # PAGE 1: HEADER, OVERVIEW, 3 MODELS BENCHMARK, & FORMULAS
    # ========================================================
    header_table = doc.add_table(rows=1, cols=1)
    header_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = header_table.cell(0, 0)
    cell.width = Inches(7.0)
    set_cell_background(cell, "0F294A")
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)

    p0 = cell.paragraphs[0]
    p0.paragraph_format.space_after = Pt(2)
    r0 = p0.add_run("SMARTTRACK AI  •  FYP PROTOTYPE 1 EXPLAINER")
    r0.font.bold = True
    r0.font.size = Pt(9)
    r0.font.color.rgb = RGBColor(0x76, 0xB9, 0xED)

    p_title = cell.add_paragraph()
    p_title.paragraph_format.space_before = Pt(2)
    p_title.paragraph_format.space_after = Pt(2)
    rt = p_title.add_run("What We Built: Models, Angles, Ghost Locking & Ground Fix")
    rt.font.bold = True
    rt.font.size = Pt(15)
    rt.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    p_sub = cell.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(1)
    p_sub.paragraph_format.space_after = Pt(0)
    r_sub = p_sub.add_run("A quick, simple guide to Prototype 1 — how everything works in plain English.")
    r_sub.font.size = Pt(9)
    r_sub.font.color.rgb = RGBColor(0xEE, 0xF5, 0xFC)

    doc.add_paragraph().paragraph_format.space_after = Pt(3)

    # 1. Quick Summary Box
    p_h1 = doc.add_paragraph()
    p_h1.paragraph_format.space_before = Pt(4)
    p_h1.paragraph_format.space_after = Pt(2)
    r = p_h1.add_run("1. The Goal in 30 Seconds")
    r.font.bold = True
    r.font.size = Pt(11.5)
    r.font.color.rgb = PRIMARY

    doc.add_paragraph(
        "We built a smart webcam engine that tracks an athlete during gym workouts (like squats) with zero extra sensors. "
        "It calculates joint angles in real time, locks onto the athlete so other gym-goers don't mess up the count, "
        "and handles tricky phone placement on the gym floor."
    )

    # 2. The 3 Models We Tested
    p_h2 = doc.add_paragraph()
    p_h2.paragraph_format.space_before = Pt(4)
    p_h2.paragraph_format.space_after = Pt(2)
    r = p_h2.add_run("2. The 3 MediaPipe Models (Which One We Picked & Why)")
    r.font.bold = True
    r.font.size = Pt(11.5)
    r.font.color.rgb = PRIMARY

    doc.add_paragraph(
        "Inside `run_webcam.py`, you can press '0', '1', or '2' on the keyboard to switch models on the fly. Here is how they compare:"
    )

    # Clean Table
    table = doc.add_table(rows=4, cols=5)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    cols = [Inches(1.8), Inches(1.1), Inches(1.1), Inches(1.1), Inches(1.7)]
    headers = ["Model", "File Size", "Speed (FPS)", "RAM (Memory)", "Verdict"]

    for i, h in enumerate(headers):
        c = table.cell(0, i)
        c.width = cols[i]
        set_cell_background(c, "0F294A")
        set_cell_margins(c, top=80, bottom=80, left=80, right=80)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    rows_data = [
        ("Lite (Press 0)", "5.8 MB", "~32-35 FPS", "~90 MB", "Fastest, but slight angle jitter"),
        ("Full (Press 1) ⭐", "9.4 MB", "~25-28 FPS", "~95 MB", "SELECTED: Perfect balance & rock solid"),
        ("Heavy (Press 2)", "30.7 MB", "~15-18 FPS", "~115 MB", "Accurate, but lags & heats up phone")
    ]

    for r_idx, r_data in enumerate(rows_data, start=1):
        for c_idx, val in enumerate(r_data):
            c = table.cell(r_idx, c_idx)
            c.width = cols[c_idx]
            bg = "EBF3FB" if r_idx == 2 else ("F9FAFB" if r_idx % 2 == 1 else "FFFFFF")
            set_cell_background(c, bg)
            set_cell_margins(c, top=60, bottom=60, left=80, right=80)
            p = c.paragraphs[0]
            p.paragraph_format.line_spacing = 1.05
            p.paragraph_format.space_after = Pt(0)
            if c_idx in [1, 2, 3]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(val)
            run.font.size = Pt(8.5)
            if r_idx == 2 and c_idx == 0:
                run.bold = True
                run.font.color.rgb = SECONDARY

    doc.add_paragraph().paragraph_format.space_after = Pt(2)

    # 3. Biomechanical Angles & Formulas (Simplified)
    p_h3 = doc.add_paragraph()
    p_h3.paragraph_format.space_before = Pt(4)
    p_h3.paragraph_format.space_after = Pt(2)
    r = p_h3.add_run("3. How Angles Are Calculated & On-Click Display")
    r.font.bold = True
    r.font.size = Pt(11.5)
    r.font.color.rgb = PRIMARY

    angle_box = [
        {"prefix": "• On-Click Angle Display: ", "text": "Angles don't clutter your view by default. Simply CLICK the mouse on the webcam screen (or press 'A' on your keyboard) to show or hide live joint degrees on screen.", "color": SECONDARY},
        {"prefix": "• True 3D Vector Formula: ", "text": "MediaPipe gives real 3D coordinates (X, Y, Z in meters). We find vectors from joint B to A and B to C, then use the Dot Product formula:", "color": PRIMARY},
        {"prefix": "    Angle Formula: ", "text": "Angle = arccos( (Vector_BA • Vector_BC) / (|Vector_BA| * |Vector_BC|) ) * (180 / π)", "color": SECONDARY},
        {"prefix": "• EMA Anti-Jitter Filter: ", "text": "Webcams can shake. We smooth numbers with Exponential Moving Average: Angle_smooth = 0.3 * New_Angle + 0.7 * Old_Angle. This gives buttery smooth 90° and 180° numbers.", "color": GREEN}
    ]
    add_card(doc, "Joint Angle Math & Interactive Click Feature", angle_box, border_color="0A66C2", bg_color="F4F8FC")

    # Benchmarking Chart inserted compactly
    chart_path = os.path.join(base_dir, "model_comparison.png")
    if os.path.exists(chart_path):
        p_c = doc.add_paragraph()
        p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_c.paragraph_format.space_before = Pt(2)
        p_c.paragraph_format.space_after = Pt(0)
        doc.add_picture(chart_path, width=Inches(4.2))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(2)
        r_c = p_cap.add_run("Chart 1: MediaPipe vs MoveNet (Why MediaPipe Full wins on speed and low RAM)")
        r_c.font.size = Pt(8)
        r_c.italic = True
        r_c.font.color.rgb = MUTED

    # PAGE BREAK -> PAGE 2
    doc.add_page_break()

    # ========================================================
    # PAGE 2: PERSON LOCKING, GHOST STATE & GROUND DRAWBACK FIX
    # ========================================================
    p_h4 = doc.add_paragraph()
    p_h4.paragraph_format.space_before = Pt(4)
    p_h4.paragraph_format.space_after = Pt(2)
    r = p_h4.add_run("4. Person Locking & Ghost Detection: How It Works")
    r.font.bold = True
    r.font.size = Pt(11.5)
    r.font.color.rgb = PRIMARY

    doc.add_paragraph(
        "In a public gym, people walk behind you constantly. Normal AI trackers get confused and jump to the background person, ruining your set. Here is how our solution stops that:"
    )

    lock_box = [
        {"prefix": "1. What is Person Locking? ", "text": "When you start your workout, the code takes your unique body ratio: (Shoulder Width) divided by (Torso Length). Everyone has a distinct bone proportion.", "color": PRIMARY},
        {"prefix": "2. What is Ghost Detection? ", "text": "If a friend walks directly in front of the camera and blocks you for a moment, the AI doesn't switch to them! It enters 'Ghost State' — it pauses counting, remembers where you were standing, and waits.", "color": ACCENT},
        {"prefix": "3. Instant Re-Locking: ", "text": "As soon as you reappear, the AI checks the body ratio. If it matches you, it resumes counting your reps instantly with 0 errors.", "color": GREEN}
    ]
    add_card(doc, "Solving Target-Hopping in Busy Gyms", lock_box, border_color="E67E22", bg_color="FDFBF7")

    # Person Locking diagram
    pl_path = os.path.join(base_dir, "person_locking.png")
    if os.path.exists(pl_path):
        p_c = doc.add_paragraph()
        p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_c.paragraph_format.space_before = Pt(2)
        p_c.paragraph_format.space_after = Pt(0)
        doc.add_picture(pl_path, width=Inches(4.2))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(3)
        r_c = p_cap.add_run("Diagram 1: The Person Locking State Machine (Active -> Ghost -> Re-Lock)")
        r_c.font.size = Pt(8)
        r_c.italic = True
        r_c.font.color.rgb = MUTED

    # 5. Ground Level Drawback & Sensor Fusion
    p_h5 = doc.add_paragraph()
    p_h5.paragraph_format.space_before = Pt(4)
    p_h5.paragraph_format.space_after = Pt(2)
    r = p_h5.add_run("5. The Real-Life Problem: Putting Phone on Ground & Sensor Fusion")
    r.font.bold = True
    r.font.size = Pt(11.5)
    r.font.color.rgb = PRIMARY

    ground_box = [
        {"prefix": "• The Real-World Drawback: ", "text": "Nobody brings a tripod to the gym! 95% of people put their phone on the ground, leaning back against a water bottle or dumbbell (tilted 45° up).", "color": ACCENT},
        {"prefix": "• Why Accuracy Drops: ", "text": "MediaPipe AI was trained on photos taken at eye/chest level. When you view someone from the floor looking up, their spine and legs look squished (foreshortened), skewing posture angles.", "color": PRIMARY},
        {"prefix": "• Our Sensor Fusion Fix (Prototype 2): ", "text": "Smartphones already have internal sensors (Gyroscope & Accelerometer) that know the phone's exact tilt angle relative to gravity. We build a 3D Rotation Matrix and mathematically 'flatten' the skeleton so it behaves as if filmed straight from a tripod!", "color": GREEN}
    ]
    add_card(doc, "Why Ground Level Causes Skew & How We Fix It", ground_box, border_color="27AE60", bg_color="F5FBF7")

    # Sensor Fusion diagram
    sf_path = os.path.join(base_dir, "sensor_fusion.png")
    if os.path.exists(sf_path):
        p_c = doc.add_paragraph()
        p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_c.paragraph_format.space_before = Pt(2)
        p_c.paragraph_format.space_after = Pt(0)
        doc.add_picture(sf_path, width=Inches(4.2))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(3)
        r_c = p_cap.add_run("Diagram 2: Combining Camera MediaPipe + Phone Tilt Sensors for Perfect Ground Angles")
        r_c.font.size = Pt(8)
        r_c.italic = True
        r_c.font.color.rgb = MUTED

    # 6. Conclusion
    p_concl = doc.add_paragraph()
    p_concl.paragraph_format.space_before = Pt(3)
    p_concl.paragraph_format.space_after = Pt(0)
    r_c_bold = p_concl.add_run("Summary: ")
    r_c_bold.bold = True
    r_c_bold.font.color.rgb = PRIMARY
    p_concl.add_run(
        "Prototype 1 proves MediaPipe Full delivers 25+ FPS on laptops/mobiles with tiny 95 MB RAM. "
        "With Ghost Locking stopping gym distractions and phone sensor calibration fixing ground angles, SmartTrack AI is ready for mobile app development."
    )

    out_file = "SmartTrack_Prototype_1_Easy_Guide.docx"
    doc.save(os.path.join(base_dir, out_file))
    print(f"[SUCCESS] Short, easy-to-understand 2-page document created: {out_file}")

if __name__ == "__main__":
    generate_quick_doc()
