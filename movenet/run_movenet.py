import cv2
import math
import time
import os
import sys
import psutil
import numpy as np

# We load TF Lite Interpreter
try:
    import tensorflow as tf
    Interpreter = tf.lite.Interpreter
except ImportError:
    print("[ERROR] TensorFlow is required for MoveNet.")
    print("Please run: pip install tensorflow")
    sys.exit(1)

MODELS_INFO = {
    "0": {
        "name": "Lightning (Model 0)",
        "file": "movenet_lightning.tflite",
        "size": 192,
        "desc": "Ultra fast, suitable for less complex poses"
    },
    "1": {
        "name": "Thunder (Model 1)",
        "file": "movenet_thunder.tflite",
        "size": 256,
        "desc": "Higher precision, recommended for most use cases"
    }
}

# MoveNet 17 Keypoints Connections
POSE_CONNECTIONS = [
    (0, 1), (1, 3), (0, 2), (2, 4),
    (0, 5), (0, 6), (5, 7), (7, 9),
    (6, 8), (8, 10), (5, 6), (5, 11),
    (6, 12), (11, 12), (11, 13), (13, 15),
    (12, 14), (14, 16)
]

ui_state = {"show_angles": False}

def mouse_callback(event, x, y, flags, param):
    """Toggle angles display on mouse click."""
    if event == cv2.EVENT_LBUTTONDOWN:
        ui_state["show_angles"] = not ui_state["show_angles"]

def angle_2d(a, b, c):
    """Calculate 2D angle."""
    radians = math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0])
    angle = abs(radians * 180.0 / math.pi)
    if angle > 180.0:
        angle = 360.0 - angle
    return int(angle)

def choose_model_interactive():
    print("\n" + "="*50)
    print("        MOVENET TRACKER - MODEL SELECTION")
    print("="*50)
    print("  [0] Lightning - Ultra fast, 192x192 input")
    print("  [1] Thunder   - High accuracy, 256x256 input (Default)")
    print("="*50)
    
    user_input = input("Select model [0 or 1] (Press Enter for 1): ").strip()
    if user_input in MODELS_INFO:
        return user_input
    return "1"

def draw_hud_box(frame, x, y, width, height, alpha=0.65, bg_color=(20, 20, 20)):
    sub_img = frame[y:y+height, x:x+width]
    if sub_img.shape[0] == height and sub_img.shape[1] == width:
        overlay = sub_img.copy()
        cv2.rectangle(overlay, (0, 0), (width, height), bg_color, -1)
        frame[y:y+height, x:x+width] = cv2.addWeighted(overlay, alpha, sub_img, 1.0 - alpha, 0)
        cv2.rectangle(frame, (x, y), (x + width, y + height), (80, 80, 80), 1)

def main():
    model_key = choose_model_interactive()
    info = MODELS_INFO[model_key]
    model_path = info["file"]
    
    if not os.path.exists(model_path):
        print(f"[!] {model_path} not found. Please ensure it has been downloaded.")
        sys.exit(1)
        
    print(f"\nInitializing MoveNet {info['name']}...")
    interpreter = Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    input_size = info["size"]
    input_dtype = input_details[0]['dtype']
    
    print("MoveNet Interpreter ready!")

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    window_name = f"MoveNet Tracker - {info['name']}"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setMouseCallback(window_name, mouse_callback)
    is_fullscreen = True

    process = psutil.Process(os.getpid())
    last_sys_stat_time = 0.0
    cached_cpu_proc, cached_cpu_sys, cached_ram_mb, cached_ram_sys_pct = 0.0, 0.0, 0.0, 0.0

    prev_time = time.monotonic()
    fps_list, infer_time_list = [], []

    while cap.isOpened():
        success, frame = cap.read()
        if not success: continue

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        t_infer_start = time.monotonic()

        # Prepare input image using pure OpenCV/NumPy (Extremely fast, 0% TF overhead)
        img = frame.copy()
        scale = min(input_size / w, input_size / h)
        new_w, new_h = int(w * scale), int(h * scale)
        resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        
        pad_w, pad_h = input_size - new_w, input_size - new_h
        top, bottom = pad_h // 2, pad_h - (pad_h // 2)
        left, right = pad_w // 2, pad_w - (pad_w // 2)
        padded = cv2.copyMakeBorder(resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=[0, 0, 0])
        
        input_image = np.expand_dims(padded, axis=0).astype(input_dtype)

        # Inference
        interpreter.set_tensor(input_details[0]['index'], input_image)
        interpreter.invoke()
        keypoints_with_scores = interpreter.get_tensor(output_details[0]['index'])[0, 0]

        infer_latency_ms = (time.monotonic() - t_infer_start) * 1000.0
        infer_time_list.append(infer_latency_ms)
        if len(infer_time_list) > 20: infer_time_list.pop(0)
        avg_infer_ms = sum(infer_time_list) / len(infer_time_list)

        pose_detected = False
        screen_coords = {}
        
        # Check if we have a confident detection (e.g. at least one point > 0.3)
        if np.max(keypoints_with_scores[:, 2]) > 0.3:
            pose_detected = True
            for idx in range(17):
                ky, kx, kscore = keypoints_with_scores[idx]
                if kscore > 0.3:
                    cx, cy = int(kx * w), int(ky * h)
                    screen_coords[idx] = (cx, cy)
                    cv2.circle(frame, (cx, cy), 5, (0, 100, 255), -1)
                    cv2.circle(frame, (cx, cy), 7, (255, 255, 255), 1)

            for start_idx, end_idx in POSE_CONNECTIONS:
                if start_idx in screen_coords and end_idx in screen_coords:
                    x1, y1 = screen_coords[start_idx]
                    x2, y2 = screen_coords[end_idx]
                    cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 180), 3)

            # Draw Angles if clicked
            if ui_state.get("show_angles", False):
                # MoveNet joint definitions for angle computation
                joint_defs = [
                    ("L-Elbow", 5, 7, 9), ("R-Elbow", 6, 8, 10),
                    ("L-Shoulder", 7, 5, 11), ("R-Shoulder", 8, 6, 12),
                    ("L-Hip", 5, 11, 13), ("R-Hip", 6, 12, 14),
                    ("L-Knee", 11, 13, 15), ("R-Knee", 12, 14, 16)
                ]
                for name, a, b, c in joint_defs:
                    if a in screen_coords and b in screen_coords and c in screen_coords:
                        angle_val = angle_2d(screen_coords[a], screen_coords[b], screen_coords[c])
                        bx, by = screen_coords[b]
                        text = f"{angle_val}"
                        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
                        cv2.rectangle(frame, (bx + 8, by - 14), (bx + 12 + tw, by + 4), (0, 0, 0), -1)
                        cv2.putText(frame, text, (bx + 10, by), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1, cv2.LINE_AA)

        # FPS
        curr_time = time.monotonic()
        fps = 1.0 / (curr_time - prev_time + 1e-6)
        prev_time = curr_time
        fps_list.append(fps)
        if len(fps_list) > 15: fps_list.pop(0)
        avg_fps = sum(fps_list) / len(fps_list)

        if curr_time - last_sys_stat_time > 0.5:
            try:
                cached_cpu_proc = process.cpu_percent()
                cached_cpu_sys = psutil.cpu_percent()
                cached_ram_mb = process.memory_info().rss / (1024 * 1024)
                cached_ram_sys_pct = psutil.virtual_memory().percent
            except Exception: pass
            last_sys_stat_time = curr_time

        # HUD
        hud_w, hud_h, hud_x, hud_y = min(w - 20, 560), 105, 10, 10
        draw_hud_box(frame, hud_x, hud_y, hud_w, hud_h, alpha=0.75, bg_color=(15, 18, 22))

        status_color = (0, 255, 128) if pose_detected else (0, 165, 255)
        status_label = "TRACKING" if pose_detected else "SEARCHING"
        cv2.putText(frame, f"MODEL: {info['name']}", (hud_x + 10, hud_y + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(frame, f"[{status_label} | 2D Only]", (hud_x + 280, hud_y + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.52, status_color, 1, cv2.LINE_AA)
        cv2.putText(frame, f"FPS: {avg_fps:.1f} ({avg_infer_ms:.1f}ms)", (hud_x + 10, hud_y + 47), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (0, 255, 220), 1, cv2.LINE_AA)
        cv2.putText(frame, f"CPU: {cached_cpu_proc:.0f}% (Sys: {cached_cpu_sys:.0f}%)", (hud_x + 240, hud_y + 47), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (220, 220, 255), 1, cv2.LINE_AA)
        cv2.putText(frame, f"RAM: {cached_ram_mb:.1f} MB (Sys: {cached_ram_sys_pct:.0f}%)", (hud_x + 10, hud_y + 72), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (255, 200, 100), 1, cv2.LINE_AA)
        cv2.putText(frame, f"Res: {w}x{h}", (hud_x + 240, hud_y + 72), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (180, 180, 180), 1, cv2.LINE_AA)
        cv2.putText(frame, "'f': Fullscreen | 'q': Quit | CLICK: Toggle Angles", (hud_x + 10, hud_y + 96), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (160, 160, 160), 1, cv2.LINE_AA)

        cv2.imshow(window_name, frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27: break
        elif key == ord('f'):
            is_fullscreen = not is_fullscreen
            prop = cv2.WINDOW_FULLSCREEN if is_fullscreen else cv2.WINDOW_NORMAL
            cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, prop)

    cap.release()
    cv2.destroyAllWindows()
    print("Exited cleanly.")

if __name__ == "__main__":
    main()
