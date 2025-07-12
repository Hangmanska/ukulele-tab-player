
import cv2
import pyrealsense2 as rs
import numpy as np
import mediapipe as mp

# Init RealSense
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

# Init MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

FINGER_TIPS = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky

print("🟢 เริ่มต้นระบบคาลิเบรต Mapping กล้อง → fretboard แล้ว")

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

        if results.multi_hand_landmarks and results.multi_handedness:
            for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                handedness = results.multi_handedness[i].classification[0].label
                if handedness != "Left":
                    continue  # โฟกัสเฉพาะมือซ้าย

                for idx in FINGER_TIPS:
                    lm = hand_landmarks.landmark[idx]
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    print(f"🔹 ปลายนิ้ว {idx} (x={cx}, y={cy})")
                    cv2.circle(frame, (cx, cy), 8, (0, 255, 255), -1)
                    cv2.putText(frame, str(idx), (cx+5, cy-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)

                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        cv2.imshow("🎯 Calibrate Fretboard Mapping", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # กด ESC เพื่อออก
            break

finally:
    pipeline.stop()
    cv2.destroyAllWindows()
