import cv2
import mediapipe as mp
import math
import time
import os
import sys
import psutil
import urllib.request
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Available Models mapping
MODELS_INFO = {
    "0": {
        "name": "Lite (Model 0)",
        "file": "pose_landmarker_lite.task",
        "url": "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task",
        "desc": "Fastest inference, lower CPU/RAM usage"
    },
    "1": {
        "name": "Full (Model 1)",
        "file": "pose_landmarker_full.task",
        "url": "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task",
        "desc": "Balanced performance & precision (recommended)"
    },
    "2": {
        "name": "Heavy (Model 2)",
        "file": "pose_landmarker_heavy.task",
        "url": "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/latest/pose_landmarker_heavy.task",
        "desc": "Highest accuracy, deeper neural network"
    }
}

# 33 BlazePose Skeletal Connections
POSE_CONNECTIONS = [
    # Face
    (0, 1), (1, 2), (2, 3), (3, 7),
    (0, 4), (4, 5), (5, 6), (6, 8),
    (9, 10),
    # Torso
    (11, 12), (11, 23), (12, 24), (23, 24),
    # Left Arm
    (11, 13), (13, 15), (15, 17), (15, 19), (15, 21), (17, 19),
    # Right Arm
    (12, 14), (14, 16), (16, 18), (16, 20), (16, 22), (18, 20),
    # Left Leg
    (23, 25), (25, 27), (27, 29), (27, 31), (29, 31),
    # Right Leg
    (24, 26), (26, 28), (28, 30), (28, 32), (30, 32)
]

# Global state for UI interaction
ui_state = {"show_angles": False}

def mouse_callback(event, x, y, flags, param):
    """Toggle angles display on mouse click."""
    if event == cv2.EVENT_LBUTTONDOWN:
        ui_state["show_angles"] = not ui_state["show_angles"]

class EMAFilter:
    """Exponential Moving Average filter to smooth out shaky angles."""
    def __init__(self, alpha=0.3):
        self.alpha = alpha
        self.value = None

    def update(self, new_value):
        if self.value is None:
            self.value = new_value
        else:
            self.value = (self.alpha * new_value) + ((1.0 - self.alpha) * self.value)
        return int(self.value)


class SquatRepCounter:
    """State machine with hysteresis for counting squat reps."""
    def __init__(self, down_threshold=90, up_threshold=150):
        self.down_threshold = down_threshold
        self.up_threshold = up_threshold
        self.reps = 0
        self.state = "UP"  # Can be "UP" or "DOWN"

    def update(self, angle):
        if angle < self.down_threshold and self.state == "UP":
            self.state = "DOWN"
        elif angle > self.up_threshold and self.state == "DOWN":
            self.state = "UP"
            self.reps += 1
        return self.reps, self.state


class MorphologicalLocker:
    def __init__(self, tolerance=0.15):
        self.locked_signature = None
        self.tolerance = tolerance
        self.ghost_mode = False

    def calculate_signature(self, world_landmarks):
        if not world_landmarks: return None
        l_sh, r_sh = world_landmarks[11], world_landmarks[12]
        l_hip, r_hip = world_landmarks[23], world_landmarks[24]
        
        def dist(a, b): return math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2 + (a.z-b.z)**2)
        def dist_tuple(a, b): return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2)
        
        shoulder_width = dist(l_sh, r_sh)
        mid_sh = ((l_sh.x+r_sh.x)/2, (l_sh.y+r_sh.y)/2, (l_sh.z+r_sh.z)/2)
        mid_hip = ((l_hip.x+r_hip.x)/2, (l_hip.y+r_hip.y)/2, (l_hip.z+r_hip.z)/2)
        torso_length = dist_tuple(mid_sh, mid_hip)
        
        if torso_length == 0: return None
        return shoulder_width / torso_length

    def check_lock(self, world_landmarks):
        sig = self.calculate_signature(world_landmarks)
        if not sig: return False
        
        if self.locked_signature is None:
            self.locked_signature = sig
            self.ghost_mode = False
            return True
            
        error = abs(sig - self.locked_signature) / self.locked_signature
        if error <= self.tolerance:
            self.ghost_mode = False
            self.locked_signature = 0.9 * self.locked_signature + 0.1 * sig
            return True
        else:
            self.ghost_mode = True
            return False


def angle_3d(a, b, c):
    """Calculate TRUE 3D angle at joint B using world landmarks (x,y,z in meters)."""
    ba_x, ba_y, ba_z = a[0] - b[0], a[1] - b[1], a[2] - b[2]
    bc_x, bc_y, bc_z = c[0] - b[0], c[1] - b[1], c[2] - b[2]

    dot = ba_x * bc_x + ba_y * bc_y + ba_z * bc_z
    mag_ba = math.sqrt(ba_x**2 + ba_y**2 + ba_z**2)
    mag_bc = math.sqrt(bc_x**2 + bc_y**2 + bc_z**2)

    if mag_ba < 1e-6 or mag_bc < 1e-6:
        return 0

    cos_angle = max(-1.0, min(1.0, dot / (mag_ba * mag_bc)))
    return int(math.degrees(math.acos(cos_angle)))


def angle_2d(a, b, c):
    """Fallback 2D angle (screen coordinates) if world landmarks unavailable."""
    radians = math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0])
    angle = abs(radians * 180.0 / math.pi)
    if angle > 180.0:
        angle = 360.0 - angle
    return int(angle)


def ensure_model_file(model_choice):
    """Checks if model file exists locally; downloads if missing."""
    info = MODELS_INFO.get(model_choice, MODELS_INFO["1"])
    filename = info["file"]
    
    if not os.path.exists(filename):
        print(f"\n[!] Model file '{filename}' not found locally.")
        print(f"Downloading {info['name']} from Google storage...")
        try:
            urllib.request.urlretrieve(info["url"], filename)
            print(f"[✓] Download completed: {filename}\n")
        except Exception as e:
            print(f"[X] Download failed: {e}")
            if model_choice != "1" and os.path.exists("pose_landmarker_full.task"):
                print("Falling back to existing pose_landmarker_full.task")
                return "pose_landmarker_full.task", MODELS_INFO["1"]["name"]
            sys.exit(1)
            
    return filename, info["name"]


def choose_model_interactive():
    """Asks user which model to use (0 or 1)."""
    # Check if passed as command line argument
    if len(sys.argv) > 1 and sys.argv[1] in MODELS_INFO:
        choice = sys.argv[1]
        print(f"Using model selected via argument: [{choice}] {MODELS_INFO[choice]['name']}")
        return choice

    print("\n" + "="*50)
    print("      MEDIAPIPE POSE TRACKER - MODEL SELECTION")
    print("="*50)
    print("  [0] Lite  - Fastest, Lowest CPU & RAM usage")
    print("  [1] Full  - Balanced, High accuracy (Default)")
    print("  [2] Heavy - Highest accuracy, deep network")
    print("="*50)
    
    user_input = input("Select model [0, 1, or 2] (Press Enter for 1): ").strip()
    if user_input in MODELS_INFO:
        return user_input
    elif user_input == "":
        return "1"
    else:
        print(f"Invalid option '{user_input}'. Defaulting to [1] Full.")
        return "1"


def draw_hud_box(frame, x, y, width, height, alpha=0.65, bg_color=(20, 20, 20)):
    """Draws a semi-transparent HUD background."""
    sub_img = frame[y:y+height, x:x+width]
    overlay = sub_img.copy()
    cv2.rectangle(overlay, (0, 0), (width, height), bg_color, -1)
    frame[y:y+height, x:x+width] = cv2.addWeighted(overlay, alpha, sub_img, 1.0 - alpha, 0)
    cv2.rectangle(frame, (x, y), (x + width, y + height), (80, 80, 80), 1)


def main():
    model_key = choose_model_interactive()
    model_path, model_name = ensure_model_file(model_key)
    
    print(f"\nInitializing {model_name}...")

    # Initialize MediaPipe PoseLandmarker
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_poses=1,
        min_pose_detection_confidence=0.35,
        min_pose_presence_confidence=0.3,
        min_tracking_confidence=0.3
    )

    landmarker = vision.PoseLandmarker.create_from_options(options)
    print("MediaPipe Pose Landmarker ready!")

    # Open Webcam (0 is default camera)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    # Set camera resolution (480p — optimal for real-time tracking)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Fullscreen window setup
    window_name = f"MediaPipe Tracker - {model_name}"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setMouseCallback(window_name, mouse_callback)
    is_fullscreen = True

    # Process metrics setup
    process = psutil.Process(os.getpid())
    last_sys_stat_time = 0.0
    cached_cpu_proc = 0.0
    cached_cpu_sys = 0.0
    cached_ram_mb = 0.0
    cached_ram_sys_pct = 0.0

    # Monotonic clock & performance stats
    start_real = time.monotonic()
    fps_list = []
    infer_time_list = []
    prev_time = time.monotonic()

    # Gym tracking add-ons
    knee_filter = EMAFilter(alpha=0.3)
    squat_counter = SquatRepCounter()
    morph_locker = MorphologicalLocker(tolerance=0.15)

    print("\n--- GYM POSE TRACKER RUNNING ---")
    print(f"Active Model: {model_name}")
    print("Controls: 'f' = toggle fullscreen, 'q' or 'ESC' = quit\n")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            continue

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        # Measure inference latency
        t_infer_start = time.monotonic()

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        timestamp_ms = int((time.monotonic() - start_real) * 1000)

        results = landmarker.detect_for_video(mp_image, timestamp_ms)
        infer_latency_ms = (time.monotonic() - t_infer_start) * 1000.0
        infer_time_list.append(infer_latency_ms)
        if len(infer_time_list) > 20:
            infer_time_list.pop(0)
        avg_infer_ms = sum(infer_time_list) / len(infer_time_list)

        pose_detected = False
        ghost_mode_active = False
        if results.pose_landmarks and len(results.pose_landmarks) > 0:
            landmarks = results.pose_landmarks[0]
            has_world = (results.pose_world_landmarks and len(results.pose_world_landmarks) > 0)
            world = results.pose_world_landmarks[0] if has_world else None

            # --- MORPHOLOGICAL PERSON LOCKING ---
            if world:
                if not morph_locker.check_lock(world):
                    ghost_mode_active = True
            
            if ghost_mode_active:
                cv2.putText(frame, "GHOST STATE: Imposter Rejected", (30, h - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
            else:
                pose_detected = True

                # Precompute screen coords
                screen_coords = {}
            for idx, lm in enumerate(landmarks):
                if lm.visibility > 0.15:
                    screen_coords[idx] = (int(lm.x * w), int(lm.y * h))

            # Draw Skeleton
            for start_idx, end_idx in POSE_CONNECTIONS:
                if start_idx in screen_coords and end_idx in screen_coords:
                    pt1 = landmarks[start_idx]
                    pt2 = landmarks[end_idx]
                    x1, y1 = screen_coords[start_idx]
                    x2, y2 = screen_coords[end_idx]
                    color = (0, 255, 180) if (pt1.visibility > 0.35 and pt2.visibility > 0.35) else (0, 200, 255)
                    cv2.line(frame, (x1, y1), (x2, y2), color, 3)

            for idx, coords in screen_coords.items():
                cx, cy = coords
                cv2.circle(frame, (cx, cy), 5, (0, 100, 255), -1)
                cv2.circle(frame, (cx, cy), 7, (255, 255, 255), 1)

            # Knee Angle for Squat Rep Counter
            def get_angle(idx_a, idx_b, idx_c):
                if (landmarks[idx_a].visibility > 0.2 and
                    landmarks[idx_b].visibility > 0.2 and
                    landmarks[idx_c].visibility > 0.2):
                    if world:
                        a = (world[idx_a].x, world[idx_a].y, world[idx_a].z)
                        b = (world[idx_b].x, world[idx_b].y, world[idx_b].z)
                        c = (world[idx_c].x, world[idx_c].y, world[idx_c].z)
                        return angle_3d(a, b, c)
                    else:
                        a = (landmarks[idx_a].x * w, landmarks[idx_a].y * h)
                        b = (landmarks[idx_b].x * w, landmarks[idx_b].y * h)
                        c = (landmarks[idx_c].x * w, landmarks[idx_c].y * h)
                        return angle_2d(a, b, c)
                return None

            ang = get_angle(23, 25, 27)
            if ang is not None:
                smooth_ang = knee_filter.update(ang)
                squat_counter.update(smooth_ang)

            # Draw All Joint Angles if toggled
            if ui_state.get("show_angles", False):
                joint_definitions = [
                    ("L-Elbow", 11, 13, 15), ("R-Elbow", 12, 14, 16),
                    ("L-Shoulder", 13, 11, 23), ("R-Shoulder", 14, 12, 24),
                    ("L-Hip", 11, 23, 25), ("R-Hip", 12, 24, 26),
                    ("L-Knee", 23, 25, 27), ("R-Knee", 24, 26, 28)
                ]
                for name, a, b, c in joint_definitions:
                    angle_val = get_angle(a, b, c)
                    if angle_val is not None and b in screen_coords:
                        bx, by = screen_coords[b]
                        # Draw angle with a nice background badge for readability
                        text = f"{angle_val}"
                        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
                        cv2.rectangle(frame, (bx + 8, by - 14), (bx + 12 + tw, by + 4), (0, 0, 0), -1)
                        cv2.putText(frame, text, (bx + 10, by),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1, cv2.LINE_AA)

        # FPS calculation
        curr_time = time.monotonic()
        fps = 1.0 / (curr_time - prev_time + 1e-6)
        prev_time = curr_time
        fps_list.append(fps)
        if len(fps_list) > 15:
            fps_list.pop(0)
        avg_fps = sum(fps_list) / len(fps_list)

        # Update CPU / RAM stats every 0.5s to minimize overhead
        if curr_time - last_sys_stat_time > 0.5:
            try:
                cached_cpu_proc = process.cpu_percent()
                cached_cpu_sys = psutil.cpu_percent()
                cached_ram_mb = process.memory_info().rss / (1024 * 1024)
                cached_ram_sys_pct = psutil.virtual_memory().percent
            except Exception:
                pass
            last_sys_stat_time = curr_time

        # ===== TOP TELEMETRY & STATS HUD =====
        hud_w = min(w - 20, 560)
        hud_h = 105
        hud_x = 10
        hud_y = 10
        draw_hud_box(frame, hud_x, hud_y, hud_w, hud_h, alpha=0.75, bg_color=(15, 18, 22))

        # Row 1: Model, Mode & FPS
        mode_text = "3D" if (pose_detected and results.pose_world_landmarks and len(results.pose_world_landmarks) > 0) else "2D"
        
        if ghost_mode_active:
            status_color = (0, 0, 255)
            status_label = "GHOST STATE"
        elif pose_detected:
            status_color = (0, 255, 128)
            status_label = "LOCKED"
        else:
            status_color = (0, 165, 255)
            status_label = "SEARCHING"
        
        cv2.putText(frame, f"MODEL: {model_name}", (hud_x + 10, hud_y + 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(frame, f"[{status_label} | {mode_text}]", (hud_x + 280, hud_y + 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.52, status_color, 1, cv2.LINE_AA)

        # Row 2: FPS, Latency, CPU
        cv2.putText(frame, f"FPS: {avg_fps:.1f} ({avg_infer_ms:.1f}ms)", (hud_x + 10, hud_y + 47),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.50, (0, 255, 220), 1, cv2.LINE_AA)
        cv2.putText(frame, f"CPU: {cached_cpu_proc:.0f}% (Sys: {cached_cpu_sys:.0f}%)", (hud_x + 240, hud_y + 47),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.50, (220, 220, 255), 1, cv2.LINE_AA)
        
        # Row 3: RAM Usage
        cv2.putText(frame, f"RAM: {cached_ram_mb:.1f} MB (Sys: {cached_ram_sys_pct:.0f}%)", (hud_x + 10, hud_y + 72),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.50, (255, 200, 100), 1, cv2.LINE_AA)
        cv2.putText(frame, f"Res: {w}x{h}", (hud_x + 240, hud_y + 72),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.50, (180, 180, 180), 1, cv2.LINE_AA)

        # Row 4: Exercise Reps & Controls
        state_color = (0, 255, 255) if squat_counter.state == "DOWN" else (0, 255, 0)
        cv2.putText(frame, f"SQUAT REPS: {squat_counter.reps} [{squat_counter.state}]", (hud_x + 10, hud_y + 96),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.58, state_color, 2, cv2.LINE_AA)
        cv2.putText(frame, "'f': Fullscreen | 'q': Quit | CLICK: Toggle Angles", (hud_x + 240, hud_y + 96),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (160, 160, 160), 1, cv2.LINE_AA)

        cv2.imshow(window_name, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break
        elif key == ord('f'):
            is_fullscreen = not is_fullscreen
            prop = cv2.WINDOW_FULLSCREEN if is_fullscreen else cv2.WINDOW_NORMAL
            cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, prop)

    cap.release()
    cv2.destroyAllWindows()
    landmarker.close()
    print("Webcam released. Exited cleanly.")


if __name__ == "__main__":
    main()
