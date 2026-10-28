import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import datetime

def set_cell_background(cell, fill_hex):
    """Sets background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Sets internal padding for a cell (in dxa)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}>'
                      f'<w:top w:w="{top}" w:type="dxa"/>'
                      f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
                      f'<w:left w:w="{left}" w:type="dxa"/>'
                      f'<w:right w:w="{right}" w:type="dxa"/>'
                      f'</w:tcMar>')
    tcPr.append(tcMar)

def create_callout_box(doc, text_paragraphs, border_color="0A66C2", bg_color="F4F8FC"):
    """Creates a beautifully styled callout box with a colored left border."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=160)
    
    # Left border only
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}>'
                          f'<w:top w:val="none"/>'
                          f'<w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/>'
                          f'<w:bottom w:val="none"/>'
                          f'<w:right w:val="none"/>'
                          f'</w:tcBorders>')
    tcPr.append(tcBorders)
    
    # Populate cell
    p_first = cell.paragraphs[0]
    p_first.paragraph_format.space_before = Pt(0)
    p_first.paragraph_format.space_after = Pt(4)
    p_first.paragraph_format.line_spacing = 1.15
    
    for i, line_data in enumerate(text_paragraphs):
        if i == 0:
            p = p_first
        else:
            p = cell.add_paragraph()
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = 1.15
            
        is_bold = line_data.get('bold', False)
        is_italic = line_data.get('italic', False)
        text = line_data.get('text', '')
        font_size = line_data.get('size', 10)
        color = line_data.get('color', RGBColor(0x22, 0x22, 0x22))
        
        run = p.add_run(text)
        run.bold = is_bold
        run.italic = is_italic
        run.font.name = 'Calibri'
        run.font.size = Pt(font_size)
        run.font.color.rgb = color

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def build_report():
    doc = Document()
    base_dir = r"c:\Users\ATIF\Desktop\fyp project\prototype 1"

    # Set page margins (0.75 in = 1.9 cm) to look elegant and balanced
    for s in doc.sections:
        s.top_margin = Inches(0.7)
        s.bottom_margin = Inches(0.7)
        s.left_margin = Inches(0.75)
        s.right_margin = Inches(0.75)

    # Color Palette Constants
    PRIMARY = RGBColor(0x0F, 0x29, 0x4A)      # Deep Navy Blue
    SECONDARY = RGBColor(0x0A, 0x66, 0xC2)    # Electric / Tech Blue
    ACCENT = RGBColor(0xD9, 0x38, 0x1E)       # Coral Accent
    DARK_TEXT = RGBColor(0x22, 0x22, 0x22)    # Charcoal body text
    MUTED = RGBColor(0x66, 0x66, 0x66)        # Gray

    # Default Style Tweaks
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(10.5)
    normal_style.font.color.rgb = DARK_TEXT
    normal_style.paragraph_format.line_spacing = 1.2
    normal_style.paragraph_format.space_after = Pt(5)

    # ==========================================
    # HEADER / BANNER
    # ==========================================
    header_table = doc.add_table(rows=1, cols=1)
    header_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    h_cell = header_table.cell(0, 0)
    h_cell.width = Inches(7.0)
    set_cell_background(h_cell, "0F294A")
    set_cell_margins(h_cell, top=200, bottom=200, left=240, right=240)
    
    p_tag = h_cell.paragraphs[0]
    p_tag.paragraph_format.space_after = Pt(2)
    r_tag = p_tag.add_run("SMARTTRACK AI  •  FINAL YEAR PROJECT (FYP) TECHNICAL REPORT")
    r_tag.font.name = 'Calibri'
    r_tag.font.size = Pt(9.5)
    r_tag.font.bold = True
    r_tag.font.color.rgb = RGBColor(0x76, 0xB9, 0xED)

    p_title = h_cell.add_paragraph()
    p_title.paragraph_format.space_before = Pt(4)
    p_title.paragraph_format.space_after = Pt(4)
    r_title = p_title.add_run("Prototype 1: MediaPipe Model Selection,\nBiomechanical Telemetry & Ground Calibration")
    r_title.font.name = 'Calibri'
    r_title.font.size = Pt(17)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    p_meta = h_cell.add_paragraph()
    p_meta.paragraph_format.space_before = Pt(4)
    p_meta.paragraph_format.space_after = Pt(0)
    r_meta = p_meta.add_run(f"Author / Candidate: Atif  |  Date: {datetime.date.today().strftime('%B %d, %Y')}  |  Framework: Python / MediaPipe / OpenCV / TFLite")
    r_meta.font.name = 'Calibri'
    r_meta.font.size = Pt(9)
    r_meta.font.color.rgb = RGBColor(0xCC, 0xDD, 0xEE)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # ==========================================
    # EXECUTIVE SUMMARY
    # ==========================================
    h1 = doc.add_paragraph()
    h1.paragraph_format.space_before = Pt(8)
    h1.paragraph_format.space_after = Pt(4)
    r = h1.add_run("1. Executive Summary & Prototype Objectives")
    r.font.name = 'Calibri'
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = PRIMARY

    p_exec = doc.add_paragraph(
        "SmartTrack AI aims to deliver an intelligent, zero-wearable computer vision coach deployed directly on mobile edge devices. "
        "The objective of Prototype 1 was to empirically benchmark state-of-the-art edge pose estimation networks, engineer an interactive biomechanical angle calculator, "
        "and resolve two critical real-world gym hurdles: (1) perspective foreshortening when a smartphone rests on the gym floor, and (2) background target hopping in crowded gym spaces."
    )
    p_exec.paragraph_format.space_after = Pt(6)

    # Bullet Highlights
    bullets = [
        ("Multi-Model Benchmark: ", "Conducted a head-to-head empirical stress test of MediaPipe Pose (Lite, Full, Heavy) vs MoveNet (Lightning, Thunder) analyzing latency (ms), frame rate (FPS), and memory footprint (MB)."),
        ("Interactive Biomechanical HUD: ", "Real-time 3D vector calculation of elbow and knee kinematics, smoothed with Exponential Moving Average (EMA) and toggleable on-screen via mouse click or hotkey."),
        ("Morphological Person Locking: ", "Custom biometric ratio algorithm (shoulder-width to torso-length) paired with a 'Ghost Mode' state machine to eliminate cross-subject interference."),
        ("Sensor-Fusion Ground Calibration: ", "Proposed mathematical fusion using smartphone IMU orientation matrices to rectify oblique low-angle camera perspective distortions.")
    ]
    for prefix, body in bullets:
        bp = doc.add_paragraph(style='List Bullet')
        bp.paragraph_format.space_before = Pt(0)
        bp.paragraph_format.space_after = Pt(3)
        bp.paragraph_format.line_spacing = 1.15
        r_pre = bp.add_run(prefix)
        r_pre.bold = True
        r_pre.font.color.rgb = SECONDARY
        r_txt = bp.add_run(body)
        r_txt.font.color.rgb = DARK_TEXT

    # ==========================================
    # SECTION 2: 3-MODEL SELECTION & BENCHMARK
    # ==========================================
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("2. Pose Estimation Model Architecture & Empirical Benchmarks")
    r.font.name = 'Calibri'
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = PRIMARY

    doc.add_paragraph(
        "We surveyed six prominent pose estimation models (OpenPose, AlphaPose, HRNet, YOLOv8, MoveNet, and MediaPipe). "
        "Due to strict edge hardware constraints (thermal stability, memory budgets < 150 MB, battery conservation), heavy top-down architectures were eliminated. "
        "We then conducted empirical comparative benchmarks across three MediaPipe Landmarker tiers alongside MoveNet variants:"
    )

    # Benchmark Table
    table = doc.add_table(rows=6, cols=6)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    headers = ["Model Variant", "Parameters / Task File", "Inference Latency", "Avg FPS (Edge)", "RAM Footprint", "Kinematic Fidelity"]
    col_widths = [Inches(1.6), Inches(1.3), Inches(1.0), Inches(0.9), Inches(1.0), Inches(1.2)]

    # Header Row
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].width = col_widths[i]
        set_cell_background(hdr_cells[i], "0F294A")
        set_cell_margins(hdr_cells[i], top=100, bottom=100, left=100, right=100)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(title)
        run.bold = True
        run.font.size = Pt(8.5)
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    # Data Rows
    data = [
        ("MediaPipe Lite", "5.8 MB (.task)", "28.5 ms", "32-35 FPS", "90 MB", "Moderate (Jitter in fast reps)"),
        ("MediaPipe Full (Selected)", "9.4 MB (.task)", "36.2 ms", "25-28 FPS", "95 MB", "High (True 3D Metric Coords)"),
        ("MediaPipe Heavy", "30.7 MB (.task)", "62.4 ms", "15-18 FPS", "115 MB", "Maximum (High thermal load)"),
        ("MoveNet Lightning", "4.8 MB (.tflite)", "25.0 ms", "32 FPS", "420 MB", "Poor (2D only, severe skew)"),
        ("MoveNet Thunder", "12.6 MB (.tflite)", "41.0 ms", "22 FPS", "450 MB", "Moderate (2D only, high RAM)")
    ]

    for row_idx, row_data in enumerate(data, start=1):
        row_cells = table.rows[row_idx].cells
        bg_col = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
        if "Selected" in row_data[0]:
            bg_col = "EBF3FB"
        for col_idx, cell_value in enumerate(row_data):
            row_cells[col_idx].width = col_widths[col_idx]
            set_cell_background(row_cells[col_idx], bg_col)
            set_cell_margins(row_cells[col_idx], top=80, bottom=80, left=90, right=90)
            p = row_cells[col_idx].paragraphs[0]
            p.paragraph_format.line_spacing = 1.05
            p.paragraph_format.space_after = Pt(0)
            if col_idx in [2, 3, 4]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(cell_value)
            run.font.size = Pt(8.5)
            if "Selected" in row_data[0] and col_idx == 0:
                run.bold = True
                run.font.color.rgb = SECONDARY

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # Insert Benchmark Graph
    comp_img_path = os.path.join(base_dir, "model_comparison.png")
    if os.path.exists(comp_img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(4)
        p_img.paragraph_format.space_after = Pt(2)
        doc.add_picture(comp_img_path, width=Inches(5.2))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(8)
        r_cap = p_cap.add_run("Figure 1: Quantitative Edge Benchmark: FPS Throughput vs. Memory Footprint across evaluated models.")
        r_cap.font.size = Pt(8.5)
        r_cap.italic = True
        r_cap.font.color.rgb = MUTED

    # Page Break for clean 2-3 page flow
    doc.add_page_break()

    # ==========================================
    # SECTION 3: BIOMECHANICAL ANGLES & UI
    # ==========================================
    h3 = doc.add_paragraph()
    h3.paragraph_format.space_before = Pt(4)
    h3.paragraph_format.space_after = Pt(4)
    r = h3.add_run("3. Biomechanical Joint Kinematics & Interactive Angle HUD")
    r.font.name = 'Calibri'
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = PRIMARY

    doc.add_paragraph(
        "A critical innovation in Prototype 1 is transitioning away from standard 2D image-space angles to true 3D metric space angles. "
        "MediaPipe outputs `pose_world_landmarks`, which construct an anatomical reference frame centered at the subject's geometric hip midpoint with metric coordinates (x, y, z in meters)."
    )

    # Mathematical Formula Callout
    formula_callout = [
        {"text": "Mathematical Formulation: 3D Vector Angle Calculation", "bold": True, "size": 10.5, "color": PRIMARY},
        {"text": "Let joint B be the vertex (e.g., knee or elbow), connected to proximal joint A and distal joint C. We construct 3D spatial vectors:", "bold": False, "size": 9.5},
        {"text": "    v_BA = (x_A - x_B,  y_A - y_B,  z_A - z_B)    and    v_BC = (x_C - x_B,  y_C - y_B,  z_C - z_B)", "bold": True, "size": 9.5, "color": SECONDARY},
        {"text": "The angle θ is computed using the dot product formula, normalized against vector magnitudes:", "bold": False, "size": 9.5},
        {"text": "    θ = arccos( (v_BA • v_BC) / ( ||v_BA|| * ||v_BC|| ) ) * (180 / π)", "bold": True, "size": 9.5, "color": PRIMARY},
        {"text": "Jitter Smoothing via EMA Filter:  θ_smooth[t] = α * θ_raw[t] + (1 - α) * θ_smooth[t-1]  (where α = 0.30)", "bold": True, "size": 9.5, "color": ACCENT}
    ]
    create_callout_box(doc, formula_callout, border_color="0A66C2", bg_color="F4F8FC")

    # Interactive UI Features
    p_ui = doc.add_paragraph()
    p_ui.paragraph_format.space_before = Pt(4)
    r_ui_title = p_ui.add_run("Interactive Angle Telemetry (Mouse Click & Keyboard Control): ")
    r_ui_title.bold = True
    p_ui.add_run(
        "To ensure a seamless user experience, the angle visualization HUD does not clutter the video stream by default. "
        "Users can toggle real-time anatomical angle overlays directly on the display by clicking the left mouse button anywhere on the active video window, or by pressing the 'A' key on the keyboard. "
        "When enabled, dynamic bounding cards and smoothed joint labels appear adjacent to the elbows and knees, highlighting Range of Motion (RoM) in real time."
    )

    # ==========================================
    # SECTION 4: PERSON LOCKING & GHOST STATE
    # ==========================================
    h4 = doc.add_paragraph()
    h4.paragraph_format.space_before = Pt(10)
    h4.paragraph_format.space_after = Pt(4)
    r = h4.add_run("4. Person Locking Mechanism & Ghost State Handling")
    r.font.name = 'Calibri'
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = PRIMARY

    doc.add_paragraph(
        "Commercial fitness apps suffer chronically from 'Target Hopping' in public gyms. If an unmonitored individual walks behind the trainee, "
        "standard detection pipelines switch targets mid-repetition, corrupting rep counters and exercise analytics. "
        "Prototype 1 introduces a dedicated Morphological Signature Locker and a Ghost State Machine."
    )

    # Ghost Detection Explanation Callout
    ghost_callout = [
        {"text": "How Person Locking & Ghost Mode Work in Prototype 1:", "bold": True, "size": 10.5, "color": PRIMARY},
        {"text": "1. Morphological Fingerprinting: When the athlete initializes the session, the system calculates a scale-invariant ratio S:", "bold": False, "size": 9.5},
        {"text": "       S = Distance(Left_Shoulder, Right_Shoulder) / Distance(Mid_Shoulder, Mid_Hip)", "bold": True, "size": 9.5, "color": SECONDARY},
        {"text": "2. Biometric Verification: For each frame, the detected subject's ratio S_current is compared against S_locked with a 15% tolerance window (ε = 0.15).", "bold": False, "size": 9.5},
        {"text": "3. Ghost Detection State: If the trainee is completely occluded (e.g., someone walks directly in front of the lens) or steps temporarily off-camera, the tracker enters Ghost State. Rather than locking onto background gym-goers, the algorithm freezes state analytics, maintains spatial memory of the last known centroid, and waits.", "bold": False, "size": 9.5},
        {"text": "4. Re-Identification: When a subject re-emerges, the locker verifies their morphological ratio. If matched, tracking immediately resumes with zero data loss.", "bold": False, "size": 9.5}
    ]
    create_callout_box(doc, ghost_callout, border_color="E67E22", bg_color="FDFBF7")

    # Insert Person Locking Diagram
    lock_img_path = os.path.join(base_dir, "person_locking.png")
    if os.path.exists(lock_img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(4)
        p_img.paragraph_format.space_after = Pt(2)
        doc.add_picture(lock_img_path, width=Inches(5.0))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(8)
        r_cap = p_cap.add_run("Figure 2: Finite State Machine for Morphological Person Locking and Ghost State recovery.")
        r_cap.font.size = Pt(8.5)
        r_cap.italic = True
        r_cap.font.color.rgb = MUTED

    # Page Break for clean final section
    doc.add_page_break()

    # ==========================================
    # SECTION 5: REAL-WORLD DRAWBACK & SENSOR FUSION
    # ==========================================
    h5 = doc.add_paragraph()
    h5.paragraph_format.space_before = Pt(4)
    h5.paragraph_format.space_after = Pt(4)
    r = h5.add_run("5. Ground-Level Drawback & Next-Gen IMU Sensor Fusion")
    r.font.name = 'Calibri'
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = PRIMARY

    p_drawback = doc.add_paragraph()
    r_draw_title = p_drawback.add_run("The Real-World Ground-Level Drawback: ")
    r_draw_title.bold = True
    r_draw_title.font.color.rgb = ACCENT
    p_drawback.add_run(
        "In practical fitness settings, gym users rarely position their mobile devices on elevated tripods at waist height. Instead, 90% of athletes lean their phone against a water bottle, weight plate, or dumbbell resting directly on the ground level. "
        "This creates an extreme upward pitch angle (typically 35° to 65° from the horizontal floor plane)."
    )

    doc.add_paragraph(
        "Because deep neural networks are primarily trained on human figures photographed near the center of height with horizontal optical axes, "
        "low-angle ground placement introduces non-linear perspective foreshortening. While MediaPipe's neural depth estimator recovers local limb geometries well, "
        "global angles (such as torso incline, hip hinge angle, and spine neutrality relative to the floor) experience severe skew, impairing clinical biomechanical diagnosis."
    )

    # Sensor Fusion Architecture Diagram
    sensor_img_path = os.path.join(base_dir, "sensor_fusion.png")
    if os.path.exists(sensor_img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(4)
        p_img.paragraph_format.space_after = Pt(2)
        doc.add_picture(sensor_img_path, width=Inches(5.0))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(6)
        r_cap = p_cap.add_run("Figure 3: Proposed Hardware-Software Sensor Fusion Pipeline (Camera Landmarker + Phone IMU).")
        r_cap.font.size = Pt(8.5)
        r_cap.italic = True
        r_cap.font.color.rgb = MUTED

    # Sensor Fusion Solution Callout
    imu_callout = [
        {"text": "Future Hardware-Software Sensor Fusion Solution:", "bold": True, "size": 10.5, "color": PRIMARY},
        {"text": "1. Mobile IMU Telemetry: Through Android Sensor APIs, we read real-time gravity vectors, accelerometer data, and gyroscopic orientation angles (pitch θ, roll φ, yaw ψ).", "bold": False, "size": 9.5},
        {"text": "2. Coordinate Transformation Matrix (R): Construct a 3D Euler rotation matrix representing device tilt:", "bold": False, "size": 9.5},
        {"text": "       P_calibrated = R_pitch(θ) • R_roll(φ) • P_mediapipe", "bold": True, "size": 9.5, "color": SECONDARY},
        {"text": "3. Perspective Virtualization: The system mathematically rotates the user's digital skeleton in memory, aligning the ground plane with the true gravitational vector. Even if the phone is placed tilted on the floor, exercise analysis computes as if recorded by a studio-level horizontal tripod.", "bold": False, "size": 9.5}
    ]
    create_callout_box(doc, imu_callout, border_color="27AE60", bg_color="F5FBF7")

    # ==========================================
    # SECTION 6: SUMMARY & NEXT STEPS
    # ==========================================
    h6 = doc.add_paragraph()
    h6.paragraph_format.space_before = Pt(8)
    h6.paragraph_format.space_after = Pt(4)
    r = h6.add_run("6. Conclusion & Roadmap to Prototype 2")
    r.font.name = 'Calibri'
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = PRIMARY

    doc.add_paragraph(
        "Prototype 1 has validated that Google MediaPipe Full provides the optimal combination of 3D anatomical accuracy and sub-40ms edge latency. "
        "The inclusion of EMA filtering, on-click angle visualization, and morphological ghost locking creates a resilient foundation. "
        "The next phase (Prototype 2) will port this verified Python architecture into Flutter/Android NDK with native IMU sensor fusion calibration."
    )

    # Save Document
    output_filename = "SmartTrack_Prototype_1_Technical_Report.docx"
    output_path = os.path.join(base_dir, output_filename)
    doc.save(output_path)
    print(f"[SUCCESS] Beautiful technical document saved to: {output_path}")

if __name__ == "__main__":
    build_report()
