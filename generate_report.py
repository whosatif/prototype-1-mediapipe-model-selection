import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import datetime

doc = docx.Document()

style = doc.styles['Normal']
font = style.font
font.name = 'Arial'
font.size = Pt(11)

# Title Page
doc.add_heading('Final Year Project (FYP) Progress Report', 0)
doc.add_paragraph('Project Title: SmartTrack AI - Real-time Gym Pose Tracking & Analytics')
doc.add_paragraph(f'Date: {datetime.date.today().strftime("%B %d, %Y")}')
doc.add_paragraph('Status: Mid-Phase Implementation and Architectural Pivot')
doc.add_page_break()

# Executive Summary
doc.add_heading('Executive Summary', level=1)
p = doc.add_paragraph(
    "This progress report outlines the recent developmental phases, architectural pivots, and technical evaluations conducted for the SmartTrack AI project. Over the past iteration, the primary focus has been on establishing a robust, highly accurate, and performant skeletal tracking pipeline suitable for deployment on mid-range consumer hardware. This involved a rigorous head-to-head evaluation of Google's MoveNet (Lightning and Thunder variants) against MediaPipe Pose (Lite and Full models). Following extensive testing of both frameworks in real-world gym conditions, the team has strategically opted to finalize MediaPipe as the core tracking engine, discarding MoveNet due to suboptimal performance in heavily occluded environments.\n\n"
    "Furthermore, two critical architectural enhancements have been finalized and are currently under implementation: 1) A hardware-software sensor fusion approach utilizing native phone sensors (accelerometer, gyroscope, and inclinometer) to guarantee precise camera perspective calibration—even when the device is rested on the ground at arbitrary angles. 2) A persistent 'Person Locking' mechanism designed to isolate and track a single user in crowded gym spaces, persisting the target's identity even through temporary occlusions or camera disappearances. These enhancements ensure the final system aligns with the proposed standard of clinical-grade accuracy and uninterrupted user experience."
)

# Section 1
doc.add_heading('1. Introduction and Current Progress', level=1)
doc.add_paragraph(
    "The SmartTrack AI project aims to deliver a zero-hardware, computer-vision-based gym coaching application. As outlined in the original proposal, the system requires ultra-low latency and high precision to count repetitions, monitor Range of Motion (RoM), and analyze posture. The development sprint covered in this report focused strictly on the Computer Vision pipeline and the selection of the optimal edge-AI framework. We successfully built a unified benchmarking environment that allowed hot-swapping between models to analyze CPU/RAM overhead, frames-per-second (FPS), and tracking fidelity."
)

# Section 2
doc.add_heading('2. Technical Evaluation: Pose Estimation Models', level=1)

doc.add_heading('2.1 Exploration of MoveNet (Lightning and Thunder)', level=2)
doc.add_paragraph(
    "In an attempt to reduce the computational overhead of the application, the team integrated and tested TensorFlow Lite's MoveNet models. We evaluated both the Lightning (192x192 input, optimized for ultra-fast inference) and Thunder (256x256 input, optimized for accuracy) variants using Float16 quantization. "
    "While MoveNet demonstrated exceptional framerates (running consistently at >25 FPS on CPU), the tracking fidelity was ultimately deemed insufficient for the rigorous demands of fitness tracking. MoveNet operates strictly in a 2D coordinate space and lacks the depth-awareness required to accurately calculate biomechanical joint angles when the camera is placed at severe oblique angles (e.g., resting on a gym floor). Consequently, MoveNet was classified as unsuitable for the project's stringent requirements."
)

doc.add_heading('2.2 Re-evaluating MediaPipe (Lite and Full)', level=2)
doc.add_paragraph(
    "Parallel testing was conducted using Google's MediaPipe Pose Landmarker, specifically testing the Lite and Full model topologies. MediaPipe proved vastly superior for our use case. Unlike MoveNet, MediaPipe outputs pose_world_landmarks—a true 3D metric coordinate system (x, y, z in meters) that utilizes neural depth estimation. "
    "This 3D awareness allows the system to calculate true geometric joint angles using vector dot products, inherently correcting for minor camera distortions. The Full model (approx. 9MB) strikes the optimal balance, maintaining ~20-25 FPS while providing clinical-grade anatomical accuracy. Therefore, we have officially pivoted our approach to rely exclusively on the MediaPipe framework."
)

# Section 3
doc.add_heading('3. Architectural Enhancements & New Approaches', level=1)

doc.add_heading('3.1 Advanced Ground Calibration via Phone Sensors', level=2)
doc.add_paragraph(
    "A significant challenge in computer-vision gym tracking is user setup. Users typically lean their smartphones against a water bottle or on the floor, resulting in extreme upward-facing camera angles (high pitch). While MediaPipe's 3D landmarks mitigate this, severe angles can still induce foreshortening errors.\n\n"
    "To counter this, we are implementing a Sensor Fusion Calibration layer. By tapping into the mobile device's native IMU (Inertial Measurement Unit), specifically the accelerometer and gyroscope, the application will read the physical pitch and roll of the device in real-time. This hardware orientation matrix will be mathematically multiplied with the 3D landmark matrix extracted by MediaPipe. This guarantees absolute coordinate normalization. Whether the phone is perfectly vertical on a tripod or tilted 45-degrees on a gym mat, the skeletal data will be mathematically rotated to a perfect parallel plane before any RoM or posture analytics are calculated."
)

doc.add_heading('3.2 Person Locking and Re-identification', level=2)
doc.add_paragraph(
    "Gyms are highly dynamic, crowded environments. A major flaw in out-of-the-box pose trackers is 'target jumping'—if a second person walks through the frame, the tracker may latch onto them, ruining the user's set. \n\n"
    "To resolve this, we are developing a 'Person Locking' state machine. When a user initiates a set, the system will capture a baseline morphological profile (e.g., shoulder width, torso length, and bounding box centroid). The tracking pipeline is strictly clamped to a single detection. If the main user is temporarily occluded or walks out of frame, the system will enter a 'Ghost' state rather than acquiring a new target in the background. It utilizes spatial persistence to ensure that when the user steps back into the frame, the tracker verifies their morphological signature and resumes the set without data corruption."
)

# Section 4
doc.add_heading('4. Implementation Progress Status', level=1)
doc.add_paragraph(
    "To date, the following technical milestones have been successfully achieved:\n"
    "- Constructed the baseline Python/OpenCV telemetry HUD to monitor CPU, RAM, and FPS.\n"
    "- Engineered a dynamic model-switching pipeline (Lite vs. Full vs. Heavy).\n"
    "- Programmed the 3D dot-product math logic to calculate joint angles in real physical space.\n"
    "- Conclusively evaluated and deprecated the MoveNet pipeline in favor of MediaPipe.\n"
    "- Finalized the mathematical models for the upcoming Sensor Fusion and Person Locking modules."
)

# Section 5
doc.add_heading('5. Future Work and Next Steps', level=1)
doc.add_paragraph(
    "The upcoming development sprint will focus entirely on transitioning these validated Python algorithms into the native mobile application environment. The next steps include:\n"
    "1. Translating the Python MediaPipe logic into Dart/Flutter and C++ (via Android NDK).\n"
    "2. Accessing Android Platform APIs to read the IMU sensor data and applying the hardware calibration matrix.\n"
    "3. Implementing the bounding-box temporal persistence algorithm for the Person Locking feature.\n"
    "4. Integrating the squate rep-counter and EMA (Exponential Moving Average) filters into the mobile UI."
)

# Save to prototype 1 directory
doc.save(r'c:\Users\ATIF\Desktop\fyp project\prototype 1\SmartTrack_Progress_Report.docx')
print("Document generated successfully.")
