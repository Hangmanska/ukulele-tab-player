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
STRINGS = ["G", "C", "E", "A"]
FRET_COUNT = 10

# Calibration (adjust to your camera angle)
STRING_ZONES = [(100, 170), (171, 250), (251, 330), (331, 420)]  # x ranges for strings
FRET_LINES_Y = [100, 130, 160, 190, 220, 250, 280, 310, 340, 370]  # y for frets

# UI settings
FRETBOARD_WIDTH, FRETBOARD_HEIGHT = 500, 700
spacing_x = FRETBOARD_WIDTH // (len(STRINGS) + 1)
spacing_y = FRETBOARD_HEIGHT // (FRET_COUNT + 1)

def map_to_string(x):
    for i, (xmin, xmax) in enumerate(STRING_ZONES):
        if xmin <= x <= xmax:
            return i
    return None

def map_to_fret(y):
    for i, limit in enumerate(FRET_LINES_Y):
        if y < limit:
            return i
    return FRET_COUNT

def draw_fretboard(img, pressed):
    img.fill(0)
    font = cv2.FONT_HERSHEY_SIMPLEX
    for i, s in enumerate(STRINGS):
        x = spacing_x * (i + 1)
        cv2.putText(img, s, (x - 10, 30), font, 0.8, (255, 255, 255), 2)
        cv2.line(img, (x, spacing_y * 2), (x, spacing_y * (FRET_COUNT + 1)), (200, 200, 200), 2)
    for f in range(1, FRET_COUNT + 1):
        y = spacing_y * (f + 1)
        cv2.line(img, (spacing_x, y), (spacing_x * len(STRINGS), y), (200, 200, 200), 1)
        cv2.putText(img, str(f), (10, y + 5), font, 0.6, (200, 200, 200), 1)
    for idx, (string, fret) in pressed.items():
        x = spacing_x * (string + 1)
        y = spacing_y * (fret + 1)
        cv2.circle(img, (x, y), 20, (0, 255, 255), -1)
        cv2.putText(img, str(idx), (x - 10, y + 5), font, 0.8, (0, 0, 0), 2)

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

        pressed = {}

        if results.multi_hand_landmarks and results.multi_handedness:
            for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                hand_label = results.multi_handedness[i].classification[0].label
                if hand_label != "Right":
                    continue

                for idx in FINGER_TIPS:
                    lm = hand_landmarks.landmark[idx]
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    string = map_to_string(cx)
                    fret = map_to_fret(cy)
                    if string is not None:
                        pressed[idx] = (string, fret)
                        print(f"🎸 นิ้ว {idx} → สาย {STRINGS[string]} เฟรต {fret}")
                    cv2.circle(frame, (cx, cy), 6, (0, 255, 255), -1)
                    cv2.putText(frame, str(idx), (cx+5, cy-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)

        fretboard_img = np.zeros((FRETBOARD_HEIGHT, FRETBOARD_WIDTH, 3), dtype=np.uint8)
        draw_fretboard(fretboard_img, pressed)
        cam_resized = cv2.resize(frame, (FRETBOARD_WIDTH, FRETBOARD_HEIGHT))
        combined_view = np.hstack((fretboard_img, cam_resized))

        cv2.imshow("🎸 Combined Ukulele View", combined_view)
        if cv2.waitKey(1) & 0xFF == 27:
            break
finally:
    pipeline.stop()
    cv2.destroyAllWindows()
