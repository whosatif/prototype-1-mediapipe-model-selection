# Prototype 1: MediaPipe Pose Model Selection & Real-Time Telemetry

> **SmartTrack AI — Final Year Project (FYP)**  
> Real-time comparative benchmarking, model selection, and biomechanical telemetry engine powered by **Google MediaPipe Pose Landmarker** and **MoveNet**.

---

## 📌 Project Overview

This prototype serves as the core edge vision engine for **SmartTrack AI**. It evaluates and benchmarks real-time human pose estimation architectures on edge devices to select optimal models balancing **inference speed (FPS)**, **CPU/RAM footprint**, and **joint angle precision**.

### Key Features
- **Dynamic Model Selection**: Real-time switching and evaluation across **Lite**, **Full**, and **Heavy** MediaPipe Pose Landmarker models (with automated model task download).
- **Sub-Millisecond Biomechanical Angles**: Real-time calculation of key human joint kinematics:
  - Left & Right Elbow angles
  - Left & Right Knee angles
  - Shoulder / Torso alignment
- **Target Subject Locking**: Centroid-distance and bounding-box tracking to keep telemetry locked to the primary gym athlete even in crowded visual backgrounds.
- **Biomechanical Angle Jitter Reduction**: Exponential Moving Average (EMA) smoothing for stable angle estimation.
- **Comprehensive Edge Telemetry HUD**:
  - Inference Latency (ms) & Frames Per Second (FPS)
  - System Telemetry (Process RAM, System RAM, CPU Load %)
  - Interactive Angle Visualizer Overlay (toggle via Mouse Click or `'A'` key)
- **Comparative MoveNet Benchmark Module**: Includes standalone TFLite evaluation for MoveNet Lightning and MoveNet Thunder.
- **Report & Architecture Diagram Generators**: Automated generation of publication-ready comparison charts and progress reports.

---

## 🏗️ Architecture & Model Selection

### 1. Comparative Performance Benchmarks

| Model | Architecture | Target Resolution | Avg FPS (Edge/Laptop) | RAM Usage | Keypoint Precision |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **MediaPipe Lite** | BlazePose (Float16) | 256x256 | ~30 - 35 FPS | ~90 MB | Medium |
| **MediaPipe Full** *(Recommended)* | BlazePose (Float16) | 256x256 | ~25 - 28 FPS | ~95 MB | High |
| **MediaPipe Heavy** | BlazePose (Float16) | 256x256 | ~15 - 18 FPS | ~110 MB | Ultra-High |
| **MoveNet Lightning** | MobileNetV2 (TFLite) | 192x192 | ~32 FPS | ~420 MB | Standard (17 Pts) |
| **MoveNet Thunder** | MobileNetV2 (TFLite) | 256x256 | ~22 FPS | ~450 MB | High (17 Pts) |

---

## 📁 Repository Structure

```text
prototype 1/
│── run_webcam.py              # Main MediaPipe pose tracking & telemetry application
│── run.bat                    # One-click launcher script for Windows
│── requirements.txt           # Python library dependencies
│── generate_easy_doc.py       # Generates concise 2-page explainer DOCX
│── SmartTrack_Prototype_1_Easy_Guide.docx  # Concise, visual 2-page FYP guide
│── generate_technical_doc.py  # Generates comprehensive 3-page technical report
│── SmartTrack_Prototype_1_Technical_Report.docx # Detailed 3-page technical report
│── generate_diagrams.py       # Generates model comparison & sensor fusion charts
│── generate_report.py         # Automated DOCX report compilation
│── generate_long_report.py    # Detailed academic thesis progress report generator
│── movenet/
│   ├── run_movenet.py         # Comparative benchmark script for MoveNet models
│   └── run.bat                # Launcher for MoveNet benchmarks
│── LICENSE                    # MIT License
│── .gitignore                 # Excludes cache, virtual environments, and weights
└── README.md                  # Project documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.9 - 3.11** installed.
- A functional webcam or connected video device.

### 2. Installation
Clone the repository and install dependencies:

```bash
git clone https://github.com/whosatif/prototype-1-mediapipe-model-selection.git
cd prototype-1-mediapipe-model-selection
pip install -r requirements.txt
```

### 3. Run MediaPipe Pose Tracker
Simply execute:
```bash
python run_webcam.py
```
*Or double click `run.bat` on Windows.*

#### In-App Controls
- `0`: Switch to **MediaPipe Lite** (Fastest inference)
- `1`: Switch to **MediaPipe Full** (Balanced precision & speed)
- `2`: Switch to **MediaPipe Heavy** (Maximum anatomical fidelity)
- `A` or **Left Mouse Click**: Toggle joint angle overlay annotations
- `Q` or `ESC`: Exit application

---

### 4. Running the MoveNet Benchmark
To benchmark Google MoveNet:
```bash
cd movenet
python run_movenet.py
```
- `0`: MoveNet Lightning (192x192)
- `1`: MoveNet Thunder (256x256)

---

## 📊 Generating Benchmarking Charts & Reports

To regenerate performance comparison graphs and Word progress reports:
```bash
# Generate architecture and performance charts
python generate_diagrams.py

# Generate academic DOCX progress report
python generate_report.py
```

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
