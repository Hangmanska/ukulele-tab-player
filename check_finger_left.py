
import cv2
import numpy as np
import mediapipe as mp
import pyrealsense2 as rs

FINGER_TIPS = [4, 8, 12, 16, 20]

# Init MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5
)
mp_draw = mp.solutions.drawing_utils

# Init RealSense
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)
print("✅ กล้องพร้อมแล้ว")

try:
    while True:
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            continue

        frame = np.asanyarray(color_frame.get_data())
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            for i, handLms in enumerate(results.multi_hand_landmarks):
                handedness = results.multi_handedness[i].classification[0].label
                if handedness != "Left":
                    continue  # ข้ามมือขวา

                # ❌ ไม่แสดงเส้นโครงมือ
                #mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

                for idx in FINGER_TIPS:
                    lm = handLms.landmark[idx]
                    h, w, _ = frame.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (cx, cy), 8, (0, 255, 0), cv2.FILLED)
                    cv2.putText(frame, f'{idx}', (cx+5, cy-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)

        cv2.imshow("Left Hand FINGER_TIPS Detection", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

finally:
    pipeline.stop()
    cv2.destroyAllWindows()
