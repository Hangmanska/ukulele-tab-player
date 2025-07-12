import cv2
import numpy as np
import mediapipe as mp
import pyrealsense2 as rs

# MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

# RealSense setup
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

# Calibration state
calibration_mode = False
calibration_step = 0
strings_order = ["G", "C", "E", "A"]
calibration_data = {}

# Font
font = cv2.FONT_HERSHEY_SIMPLEX

print("🎬 เริ่มกล้องเรียบร้อย กด 'k' เพื่อเริ่มคาลิเบรตสาย G C E A ทีละนิ้ว")

try:
    while True:
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            continue

        frame = np.asanyarray(color_frame.get_data())
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, _ = frame.shape

        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            for lm in results.multi_hand_landmarks:
                index_tip = lm.landmark[8]
                x, y = int(index_tip.x * w), int(index_tip.y * h)
                mp_draw.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)
                cv2.circle(frame, (x, y), 10, (0, 255, 255), -1)
                cv2.putText(frame, 'Index', (x + 10, y), font, 0.5, (255, 255, 255), 1)

                if calibration_mode and calibration_step < len(strings_order):
                    string = strings_order[calibration_step]
                    cv2.putText(frame, f"แตะนิ้วชี้บนสาย {string}", (50, 50), font, 0.8, (0, 255, 255), 2)
                    calibration_data[string] = (x, y)
                    print(f"📍 คาลิเบรตสาย {string} ที่ตำแหน่ง {x}, {y}")
                    calibration_step += 1
                    if calibration_step >= len(strings_order):
                        calibration_mode = False
                        print("✅ คาลิเบรตครบ:", calibration_data)
        
        else:
            cv2.putText(frame, "ไม่พบมือ", (30, 50), font, 0.8, (0, 0, 255), 2)

        if calibration_mode and calibration_step < len(strings_order):
            cv2.putText(frame, f"คาลิเบรตสาย: {strings_order[calibration_step]}", (30, h - 20), font, 0.8, (0, 255, 255), 2)

        cv2.imshow("Calibrate Strings", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break
        elif key == ord('k'):
            print("🛠 เริ่มคาลิเบรตสาย G, C, E, A")
            calibration_mode = True
            calibration_step = 0
            calibration_data = {}

finally:
    pipeline.stop()
    cv2.destroyAllWindows()
