import cv2
import numpy as np
import mediapipe as mp
import pyrealsense2 as rs

# ตำแหน่งแนวตั้งของสาย ukulele (G C E A)
STRING_XS = [80, 180, 280, 380]  # ปรับให้ตรงกับตำแหน่งภาพ
FRET_HEIGHT = 40
FRET_COUNT = 10

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)
print("✅ กล้องพร้อมแล้ว")

def detect_string_and_fret(x, y):
    string = None
    fret = None
    for i, sx in enumerate(STRING_XS):
        if abs(x - sx) < 30:
            string = ['G', 'C', 'E', 'A'][i]
            break
    fret = int(y // FRET_HEIGHT)
    if fret > FRET_COUNT:
        fret = None
    return string, fret

try:
    while True:
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            continue
        frame = np.asanyarray(color_frame.get_data())
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = hands.process(rgb)

        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                hand_label = handedness.classification[0].label
                if hand_label == 'Right':  # มือซ้ายจากมุมมองกล้อง
                    mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    for idx in [8, 12, 16, 20]:  # fingertip: index, middle, ring, pinky
                        lm = hand_landmarks.landmark[idx]
                        x, y = int(lm.x * frame.shape[1]), int(lm.y * frame.shape[0])
                        cv2.circle(frame, (x, y), 10, (0, 255, 255), -1)
                        string, fret = detect_string_and_fret(x, y)
                        if string and fret is not None:
                            label = f'{string}{fret}'
                            cv2.putText(frame, label, (x+10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
                            print(f"🎸 นิ้ว {idx} กดสาย {string} เฟรต {fret}")
        else:
            print("🟡 ยังไม่เจอมือซ้าย")

        cv2.imshow("RealSense + MediaPipe", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

finally:
    pipeline.stop()
    cv2.destroyAllWindows()
