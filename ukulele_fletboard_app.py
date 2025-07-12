import cv2
import numpy as np
import mediapipe as mp
import pyrealsense2 as rs
import pygame
import time

# ---------------- CONFIG ----------------
WIDTH, HEIGHT = 600, 800
STRINGS = ['G', 'C', 'E', 'A']
FRET_COUNT = 10
FINGER_TIPS = [8, 12, 16, 20]  # Index, Middle, Ring, Pinky

# กำหนดตำแหน่งเส้นแนวตั้งของสาย (X)
STRING_X = [80, 180, 280, 380]

# กำหนดตำแหน่ง Y ของแต่ละเฟรต (ตามสัดส่วนกล้อง)
FRET_Y_RANGE = [(100 + i * 60, 100 + (i + 1) * 60) for i in range(FRET_COUNT)]

# ---------------- INIT PYGAME ----------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ukulele Vertical Fretboard Viewer")
font = pygame.font.SysFont("Arial", 24)
circle_font = pygame.font.SysFont("Arial", 24, bold=True)
clock = pygame.time.Clock()

def draw_fretboard(highlights):
    screen.fill((0, 0, 0))
    for i, x in enumerate(STRING_X):
        pygame.draw.line(screen, (200, 200, 200), (x, 80), (x, 80 + FRET_COUNT * 60), 2)
        label = font.render(STRINGS[i], True, (255, 255, 255))
        screen.blit(label, (x - 8, 40))
    for i in range(FRET_COUNT + 1):
        y = 80 + i * 60
        pygame.draw.line(screen, (120, 120, 120), (STRING_X[0], y), (STRING_X[-1], y), 1)
        if i < FRET_COUNT:
            label = font.render(str(i + 1), True, (180, 180, 180))
            screen.blit(label, (STRING_X[-1] + 20, y + 20))
    for s_idx, fret in highlights:
        if 0 <= fret < FRET_COUNT:
            x = STRING_X[s_idx]
            y = (FRET_Y_RANGE[fret][0] + FRET_Y_RANGE[fret][1]) // 2
            pygame.draw.circle(screen, (255, 255, 0), (x, y), 25)
            label = circle_font.render(str(fret), True, (0, 0, 0))
            rect = label.get_rect(center=(x, y))
            screen.blit(label, rect)

def get_fret_from_y(y):
    for i, (y_min, y_max) in enumerate(FRET_Y_RANGE):
        if y_min <= y < y_max:
            return i
    return None

def get_string_from_x(x):
    distances = [abs(x - sx) for sx in STRING_X]
    return np.argmin(distances)

# ---------------- INIT CAMERA + MEDIAPIPE ----------------
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

print("✅ กล้องพร้อมแล้ว")
time.sleep(1)

# ---------------- MAIN LOOP ----------------
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
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        highlights = []
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, hand_handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                if hand_handedness.classification[0].label == "Left":
                    for tip_id in FINGER_TIPS:
                        lm = hand_landmarks.landmark[tip_id]
                        x_px, y_px = int(lm.x * 640), int(lm.y * 480)
                        fret = get_fret_from_y(y_px * HEIGHT / 480)
                        string = get_string_from_x(x_px * WIDTH / 640)
                        if fret is not None:
                            highlights.append((string, fret))

        draw_fretboard(highlights)
        pygame.display.flip()
        clock.tick(30)

except KeyboardInterrupt:
    print("👋 ออกจากโปรแกรมแล้ว")

finally:
    pipeline.stop()
    pygame.quit()
