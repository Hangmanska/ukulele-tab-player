import cv2
import pyrealsense2 as rs
import numpy as np
import mediapipe as mp
import pygame
import sys

# ---------------- PYGAME SETUP ----------------
WIDTH, HEIGHT = 400, 600
STRINGS = ['G', 'C', 'E', 'A']
FRET_COUNT = 10
MARGIN = 60
STRING_X = [MARGIN + i * ((WIDTH - 2 * MARGIN) // (len(STRINGS) - 1)) for i in range(len(STRINGS))]
FRET_Y = [MARGIN + i * ((HEIGHT - 2 * MARGIN) // FRET_COUNT) for i in range(FRET_COUNT + 1)]
FINGER_RADIUS = 20

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ukulele Fretboard Debug")
font = pygame.font.SysFont("Arial", 24)

def draw_fretboard(highlight=[]):
    screen.fill((0, 0, 0))
    for i, y in enumerate(FRET_Y):
        pygame.draw.line(screen, (200, 200, 200), (MARGIN, y), (WIDTH - MARGIN, y), 2)
        if i > 0:
            screen.blit(font.render(str(i), True, (200, 200, 200)), (WIDTH - MARGIN + 10, y - 12))
    for i, (s, x) in enumerate(zip(STRINGS, STRING_X)):
        pygame.draw.line(screen, (200, 200, 200), (x, MARGIN), (x, HEIGHT - MARGIN), 2)
        screen.blit(font.render(s, True, (255, 255, 255)), (x - 10, MARGIN - 30))
    for note in highlight:
        s_idx = STRINGS.index(note["string"])
        f_idx = note["fret"]
        cx, cy = STRING_X[s_idx], FRET_Y[f_idx]
        pygame.draw.circle(screen, (255, 255, 0), (cx, cy), FINGER_RADIUS)
        screen.blit(font.render(str(f_idx), True, (0, 0, 0)), (cx - 8, cy - 14))

# ---------------- CAMERA + HAND TRACKING ----------------
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)
mp_draw = mp.solutions.drawing_utils
FINGER_TIPS = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky

# Approximate camera ↔ fretboard mapping range
string_x_range = [150, 500]
fret_y_range = [250, 500]

print("🟢 เริ่มระบบตรวจจับนิ้ว + แสดง fretboard แล้ว")

try:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise KeyboardInterrupt
        
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            continue
        frame = np.asanyarray(color_frame.get_data())
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        pressed = []
        if results.multi_hand_landmarks and results.multi_handedness:
            for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                handedness = results.multi_handedness[i].classification[0].label
                if handedness != "Left":
                    continue

                for idx in FINGER_TIPS:
                    lm = hand_landmarks.landmark[idx]
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (cx, cy), 8, (0, 255, 255), -1)
                    cv2.putText(frame, str(idx), (cx + 5, cy - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)

                    if string_x_range[0] <= cx <= string_x_range[1] and fret_y_range[0] <= cy <= fret_y_range[1]:
                        norm_x = (cx - string_x_range[0]) / (string_x_range[1] - string_x_range[0])
                        norm_y = (cy - fret_y_range[0]) / (fret_y_range[1] - fret_y_range[0])
                        string_idx = max(0, min(3, int(norm_x * len(STRINGS))))
                        fret_idx = max(0, min(FRET_COUNT, int(norm_y * FRET_COUNT)))
                        pressed.append({"string": STRINGS[string_idx], "fret": fret_idx})
                        print(f"🎸 ปลายนิ้ว {idx} กดที่สาย {STRINGS[string_idx]}, เฟรต {fret_idx}")

                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        draw_fretboard(pressed)
        pygame.display.flip()
        cv2.imshow("🎯 Calibrate Fretboard Mapping", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

finally:
    pipeline.stop()
    cv2.destroyAllWindows()
    pygame.quit()
    sys.exit()
