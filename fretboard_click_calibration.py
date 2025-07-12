import cv2
import numpy as np
import json
import pyrealsense2 as rs
import mediapipe as mp

FINGER_TIPS = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
STRINGS = ["G", "C", "E", "A"]
FRET_COUNT = 10
WIDTH, HEIGHT = 500, 700
spacing_x = WIDTH // (len(STRINGS) + 1)
spacing_y = HEIGHT // (FRET_COUNT + 1)

calibration_data = {}
selected_fret = None
last_fingertips = {}

# Init RealSense
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

# Init MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)

def draw_fretboard(img):
    img.fill(255)
    font = cv2.FONT_HERSHEY_SIMPLEX
    for i, s in enumerate(STRINGS):
        x = spacing_x * (i + 1)
        cv2.putText(img, s, (x - 10, 30), font, 0.8, (0, 0, 0), 2)
        cv2.line(img, (x, spacing_y * 2), (x, spacing_y * (FRET_COUNT + 1)), (0, 0, 0), 2)
    for f in range(1, FRET_COUNT + 1):
        y = spacing_y * (f + 1)
        cv2.line(img, (spacing_x, y), (spacing_x * len(STRINGS), y), (0, 0, 0), 1)
        cv2.putText(img, str(f), (10, y + 5), font, 0.6, (0, 0, 0), 1)

def on_mouse(event, x, y, flags, param):
    global selected_fret, last_fingertips
    if event == cv2.EVENT_LBUTTONDOWN:
        string_index = (x // spacing_x) - 1
        fret_index = (y // spacing_y) - 1
        if 0 <= string_index < 4 and 1 <= fret_index <= FRET_COUNT:
            string_name = STRINGS[string_index]
            key = f"{string_name}-{fret_index}"
            print(f"🖱️ Clicked at ({x},{y}) → คีย์: {key}")
            if last_fingertips:
                calibration_data[key] = last_fingertips.copy()
                print(f"📌 บันทึกตำแหน่งนิ้ว: {calibration_data[key]}")

cv2.namedWindow("Fretboard Calibration")
cv2.setMouseCallback("Fretboard Calibration", on_mouse)

print("🟢 เริ่มระบบคาลิเบรต โปรดชูนิ้วขวาให้กล้องเห็น และคลิกบน fretboard เพื่อตำแหน่งเฟรต")

try:
    while True:
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            continue

        frame = np.asanyarray(color_frame.get_data())
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        fingertips = {}
        if results.multi_hand_landmarks and results.multi_handedness:
            for i, handLms in enumerate(results.multi_hand_landmarks):
                handedness = results.multi_handedness[i].classification[0].label
                if handedness != "Right":
                    continue
                for idx in FINGER_TIPS:
                    lm = handLms.landmark[idx]
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    fingertips[idx] = {"x": cx, "y": cy}
                    cv2.circle(frame, (cx, cy), 6, (0, 255, 255), -1)
                    cv2.putText(frame, str(idx), (cx+5, cy-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
                last_fingertips = fingertips  # อัปเดตล่าสุด

        fretboard_img = np.ones((HEIGHT, WIDTH, 3), dtype=np.uint8) * 255
        draw_fretboard(fretboard_img)

        combined = np.hstack((fretboard_img, cv2.resize(frame, (WIDTH, HEIGHT))))
        cv2.imshow("Fretboard Calibration", combined)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            with open("calibration_points.json", "w") as f:
                json.dump(calibration_data, f, indent=2)
            print("✅ calibration_points.json บันทึกเรียบร้อยแล้ว")
            break

finally:
    pipeline.stop()
    cv2.destroyAllWindows()
