import docx
from docx.shared import Pt, Inches, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
import datetime

doc = docx.Document()

# Adjust margins to fill more pages gracefully
sections = doc.sections
for section in sections:
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(2.54)
    section.right_margin = Cm(2.54)

# Styles
style = doc.styles['Normal']
font = style.font
font.name = 'Arial'
font.size = Pt(12)
style.paragraph_format.line_spacing = 1.5

# Title Page
title = doc.add_heading('Final Year Project (FYP) Detailed Progress Report', 0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('\n\n\n')
p = doc.add_paragraph('Project Title: SmartTrack AI - Real-time Gym Pose Tracking & Analytics')
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.runs[0].font.size = Pt(16)
p.runs[0].font.bold = True

p2 = doc.add_paragraph(f'\nDate: {datetime.date.today().strftime("%B %d, %Y")}\nStatus: Comprehensive Architecture & R&D Phase Report\n')
p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_page_break()

# Executive Summary
doc.add_heading('Executive Summary', level=1)
doc.add_paragraph(
    "This extended progress report presents a comprehensive overview of the research, development, and architectural pivoting that has occurred during the initial phases of the SmartTrack AI project. The core objective of this FYP is to deliver a zero-hardware, computer-vision-based gym coaching application that operates in real-time on edge devices (smartphones) without requiring cloud processing. Achieving this requires a skeletal tracking pipeline that is not only highly accurate but also computationally lightweight."
)
doc.add_paragraph(
    "Our research journey began with a broad survey of six state-of-the-art pose estimation architectures: OpenPose, AlphaPose, HRNet, YOLOv8 Pose, MoveNet, and MediaPipe. Through a rigorous elimination process based on edge-deployability and mobile hardware constraints, we narrowed the field down to two primary candidates: Google's MoveNet and Google's MediaPipe. Subsequent head-to-head empirical testing led to the decisive selection of MediaPipe due to its unique capability to infer true 3D (Z-axis) depth coordinates, an absolute necessity for calculating biomechanical joint angles in dynamic environments."
)
doc.add_paragraph(
    "In addition to model selection, this report details two novel architectural enhancements we are introducing to solve major real-world gym tracking problems. First, we detail a 'Sensor Fusion' approach that leverages the smartphone's native IMU (accelerometer and gyroscope) to mathematically correct camera perspective distortion when the device is placed on the ground. Second, we introduce a 'Person Locking and Re-identification' state machine designed to maintain focus on the primary user in crowded environments, preventing the tracker from jumping to background individuals even when the primary user is temporarily occluded."
)

# Section 1
doc.add_heading('1. Initial Model Survey: Casting a Wide Net', level=1)
doc.add_paragraph(
    "The foundation of SmartTrack AI rests entirely on the accuracy and speed of its underlying Human Pose Estimation (HPE) model. To ensure we selected the best possible architecture, we began our research phase by analyzing six of the most prominent models in the computer vision industry:"
)
doc.add_paragraph("1. OpenPose: The pioneering multi-person pose estimation framework. While highly accurate, OpenPose utilizes a massive VGG/ResNet backbone. It requires powerful discrete GPUs to run in real-time, making it entirely unfeasible for a mobile-only application.", style='List Bullet')
doc.add_paragraph("2. AlphaPose: Known for its exceptional accuracy in crowded scenes using a top-down approach. However, similar to OpenPose, its heavy computational footprint and reliance on complex bounding-box generation pipelines disqualify it from edge deployment.", style='List Bullet')
doc.add_paragraph("3. HRNet (High-Resolution Net): Maintains high-resolution representations throughout the network for incredible precision. Unfortunately, the memory bandwidth required for HRNet causes immediate thermal throttling on standard Android devices.", style='List Bullet')
doc.add_paragraph("4. YOLOv8 Pose: The latest iteration of the Ultralytics YOLO family, now supporting keypoint detection. It is incredibly fast and highly accurate, but its TensorRT/PyTorch optimizations are better suited for desktop GPUs or dedicated edge accelerators (like Jetson Nano) rather than standard smartphone NPUs.", style='List Bullet')
doc.add_paragraph("5. MoveNet: Google's ultra-fast bottom-up pose estimation model, specifically designed for mobile and web deployment using TensorFlow Lite.", style='List Bullet')
doc.add_paragraph("6. MediaPipe Pose: Another Google framework utilizing a BlazePose topology, uniquely offering 3D landmark predictions and highly optimized cross-platform deployment.", style='List Bullet')

# Section 2
doc.add_heading('2. The Shortlist: Designing for the Edge', level=1)
doc.add_picture(r'c:\Users\ATIF\Desktop\fyp project\prototype 1\model_comparison.png', width=Inches(6))
doc.add_paragraph(
    "Given our strict project constraints—the application must run entirely offline on a standard smartphone (e.g., MediaTek Helio G88, 8GB RAM) without overheating or draining the battery rapidly—we established a strict filtration criteria. Any model requiring a discrete GPU, cloud API calls, or exhibiting a memory footprint exceeding 100MB was immediately eliminated."
)
doc.add_paragraph(
    "This elimination process swiftly removed OpenPose, AlphaPose, and HRNet. While YOLOv8 Pose showed promise, its mobile deployment pipeline via TFLite proved too unstable and memory-intensive for consistent 30 FPS tracking on lower-end devices. This left us with two highly optimized, edge-ready finalists: Google MoveNet and Google MediaPipe."
)
doc.add_paragraph(
    "To make our final decision, we built a unified Python benchmarking environment capable of hot-swapping between MoveNet (Lightning and Thunder variants) and MediaPipe (Lite and Full variants). We tested these models against real-world gym footage, measuring FPS, RAM utilization, and joint tracking stability."
)

# Section 3
doc.add_heading('3. The Head-to-Head Showdown: MoveNet vs MediaPipe', level=1)

doc.add_heading('3.1 Evaluating MoveNet (The 2D Contender)', level=2)
doc.add_paragraph(
    "We deeply integrated MoveNet into our prototype, specifically testing the Lightning (192x192 resolution) and Thunder (256x256 resolution) Float16 quantized models. MoveNet's primary advantage is its raw speed. On our CPU-bound tests, MoveNet Lightning easily achieved >30 FPS. However, as we began writing the mathematical logic for calculating joint angles (e.g., the knee angle during a squat), a critical flaw emerged."
)
doc.add_paragraph(
    "MoveNet operates strictly in a 2D coordinate space (X, Y pixels on the screen). When a user performs a squat while facing the camera slightly at an angle, the 2D projection of their leg drastically foreshortens. A true 90-degree squat might appear as a 130-degree angle on a 2D screen due to perspective distortion. MoveNet provides no depth awareness to correct this, rendering its biometric analytics highly inaccurate for out-of-plane movements. In our tests, MoveNet was classified as 'suboptimal' for clinical-grade gym tracking."
)

doc.add_heading('3.2 Evaluating MediaPipe (The 3D Champion)', level=2)
doc.add_paragraph(
    "We subsequently tested MediaPipe Pose. While slightly more computationally demanding than MoveNet Lightning, MediaPipe Full maintained a highly stable ~25 FPS, perfectly acceptable for our needs. The decisive factor, however, was MediaPipe's topological architecture. Unlike standard models, MediaPipe utilizes a secondary neural network to infer Z-axis depth, outputting a true 3D metric coordinate system (pose_world_landmarks)."
)
doc.add_paragraph(
    "By extracting the X, Y, and Z coordinates in physical space (measured in meters relative to the user's hips), we were able to calculate joint angles using 3D vector dot products. This mathematically reconstructs the true anatomical angle of the joint, entirely bypassing the 2D perspective distortion that crippled MoveNet. A 90-degree squat mathematically calculates as exactly 90 degrees, regardless of how the user is angled relative to the camera."
)

doc.add_heading('3.3 The Final Verdict', level=2)
doc.add_paragraph(
    "Based on this empirical evidence, MediaPipe Full has been officially selected as the exclusive tracking engine for SmartTrack AI. MoveNet has been permanently deprecated from our architecture. The ability to track true 3D biomechanics on a mobile device is the cornerstone that will allow our application to provide genuine, accurate coaching feedback."
)
doc.add_page_break()

# Section 4
doc.add_heading('4. Architectural Innovation: Sensor Fusion Calibration', level=1)
doc.add_picture(r'c:\Users\ATIF\Desktop\fyp project\prototype 1\sensor_fusion.png', width=Inches(6))
doc.add_paragraph(
    "A major real-world challenge in gym environments is device placement. Users rarely have access to perfectly leveled tripods; instead, they rest their smartphones on the floor, lean them against water bottles, or prop them up on benches. This results in extreme upward-facing camera angles (severe pitch). While MediaPipe's 3D landmarks mitigate localized foreshortening, a severely tilted camera frame still skews the global coordinate system, making it difficult to determine if a user's back is truly straight relative to the floor."
)

doc.add_heading('4.1 The Role of Phone Sensors', level=2)
doc.add_paragraph(
    "To solve this 'phone on the ground' problem, we are innovating beyond pure computer vision by incorporating a Hardware Sensor Fusion layer. Modern smartphones are equipped with highly accurate Inertial Measurement Units (IMUs), containing accelerometers and gyroscopes. By accessing these sensors via Android Platform APIs during the workout, the SmartTrack AI application will constantly monitor the physical pitch, roll, and yaw of the device relative to Earth's gravity vector."
)

doc.add_heading('4.2 The Mathematical Implementation', level=2)
doc.add_paragraph(
    "When a user places their phone on the ground leaning back at a 45-degree angle, the accelerometer detects this tilt. We will construct a 3x3 Rotation Matrix based on these gravity vectors. Before any fitness analytics (like back posture or squat depth) are calculated, the entire 3D skeletal matrix generated by MediaPipe will be multiplied by this hardware-derived Rotation Matrix."
)
doc.add_paragraph(
    "The result is a mathematically 'flattened' coordinate system. Even if the phone is resting on the floor looking up at the ceiling, the system rotates the user's digital skeleton in memory so it appears exactly as if it were filmed by a perfectly leveled, tripod-mounted camera. This guarantees absolute coordinate normalization and ensures our posture analytics are clinically accurate under all gym conditions."
)
doc.add_page_break()

# Section 5
doc.add_heading('5. Robustness in the Wild: Person Locking and Re-identification', level=1)
doc.add_picture(r'c:\Users\ATIF\Desktop\fyp project\prototype 1\person_locking.png', width=Inches(6))
doc.add_paragraph(
    "Gyms are inherently chaotic. A common critical failure in standard computer vision fitness apps is 'target jumping'. If a user is mid-set and another gym-goer walks through the background, standard trackers will frequently drop the main user and latch onto the background person, instantly ruining the workout data."
)

doc.add_heading('5.1 Morphological Signature Profiling', level=2)
doc.add_paragraph(
    "To combat this, we are developing a custom 'Person Locking' state machine. When the user taps 'Start Set', the system locks the tracker to num_poses=1. More importantly, it immediately captures a 'Morphological Signature' of the primary user. This signature includes proportional biometric data (e.g., shoulder-width-to-torso-length ratio) and the user's initial 3D bounding box centroid. Because humans have unique bone proportions, this signature acts as a lightweight biometric fingerprint."
)

doc.add_heading('5.2 The Ghost State Mechanism', level=2)
doc.add_paragraph(
    "If a second person walks through the frame, our spatial temporal filter rejects them because their morphological signature and bounding box velocity do not match the locked user. If the primary user is completely obscured (e.g., someone walks directly in front of the camera), the system enters a 'Ghost State'. Instead of frantically searching for a new target in the background, the tracker temporarily suspends analytics and waits."
)
doc.add_paragraph(
    "Once the occlusion passes and a human figure reappears near the last known bounding box, the system compares the new figure's bone proportions to the saved Morphological Signature. If they match, the system re-acquires the lock and resumes counting the set. This ensures the app tracks the user—and ONLY the user—until the set is completed."
)

# Conclusion
doc.add_heading('6. Conclusion and Upcoming Milestones', level=1)
doc.add_paragraph(
    "The research and prototyping phase has yielded highly successful results. By methodically eliminating unsuitable models and committing to MediaPipe, we have secured a foundation capable of true 3D biomechanical analysis. Furthermore, our designs for IMU Sensor Fusion and Person Locking address the most prominent real-world failure points of mobile fitness tracking."
)
doc.add_paragraph(
    "Moving forward, our immediate milestones are to port this validated Python logic into our native Flutter/Dart and C++ Android application. We will begin integrating the Android Sensor APIs to fetch the gravity vectors and implement the rotation matrix math in C++ for maximum efficiency. The project is currently ahead of schedule and poised to deliver a highly robust, intelligent coaching application."
)

doc.save(r'c:\Users\ATIF\Desktop\fyp project\prototype 1\SmartTrack_Progress_Report_V3.docx')
print("Detailed Document generated successfully.")
