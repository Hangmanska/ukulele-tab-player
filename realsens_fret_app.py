import cv2
import numpy as np
import mediapipe as mp
import pyrealsense2 as rs
import pygame

# ---------------- CONFIG ----------------
FINGER_TIPS = [8, 12, 16, 20]  # Index, Middle, Ring, Pinky
FINGER_NAMES = {8: "1", 12: "2", 16: "3", 20: "4"}
STRINGS = ["G", "C", "E", "A"]
NUM_FRETS = 10
SCREEN_WIDTH, SCREEN_HEIGHT = 500, 800

# Calibration range (จากภาพกล้อง)
CAMERA_X_MIN, CAMERA_X_MAX = 280, 460
CAMERA_Y_MIN, CAMERA_Y_MAX = 280, 480

# ---------------- FUNCTIONS ----------------
def camera_to_fretboard(cx, cy):
    """แปลงตำแหน่งจากกล้องเป็นตำแหน่งสายและเฟรต"""
    norm_x = (cx - CAMERA_X_MIN) / (CAMERA_X_MAX - CAMERA_X_MIN)
    norm_y = (cy - CAMERA_Y_MIN) / (CAMERA_Y_MAX - CAMERA_Y_MIN)
    norm_x = min(max(norm_x, 0), 0.999)
    norm_y = min(max(norm_y, 0), 0.999)
    string_idx = int(norm_x * len(STRINGS))
    fret = int(norm_y * NUM_FRETS)
    return string_idx, fret

def draw_fretboard(screen, pressed):
    screen.fill((0, 0, 0))
    fret_spacing = SCREEN_HEIGHT // (NUM_FRETS + 1)
    string_spacing = SCREEN_WIDTH // (len(STRINGS) + 1)

    # Draw strings
    for i, s in enumerate(STRINGS):
        x = (i + 1) * string_spacing
        pygame.draw.line(screen, (255, 255, 255), (x, fret_spacing), (x, SCREEN_HEIGHT - fret_spacing), 1)
        label = font.render(s, True, (255, 255, 255))
        screen.blit(label, (x - 10, 5))

    # Draw frets
    for i in range(1, NUM_FRETS + 1):
        y = i * fret_spacing
        pygame.draw.line(screen, (200, 200, 200), (string_spacing, y), (SCREEN_WIDTH - string_spacing, y), 1)
        label = font.render(str(i), True, (180, 180, 180))
        screen.blit(label, (5, y - 10))

    # Draw fingers
    for tip_idx, (s_idx, fret) in pressed.items():
        x = (s_idx + 1) * string_spacing
        y = (fret + 1) * fret_spacing
        pygame.draw.circle(screen, (255, 255, 0), (x, y), 20)
        label = font.render(FINGER_NAMES[tip_idx], True, (0, 0, 0))
        screen.blit(label, (x - 8, y - 12))

# ---------------- INIT ----------------
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ukulele Fretboard Debug")
font = pygame.font.SysFont("Arial", 20)

print("🎸 Ukulele Fretboard Debug พร้อมใช้งาน")
running = True

# ---------------- LOOP ----------------
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    frames = pipeline.wait_for_frames()
    color_frame = frames.get_color_frame()
    if not color_frame:
        continue
    frame = np.asanyarray(color_frame.get_data())
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    pressed = {}  # finger_tip_id : (string_idx, fret)

    if results.multi_hand_landmarks and results.multi_handedness:
        for i, handLms in enumerate(results.multi_hand_landmarks):
            handedness = results.multi_handedness[i].classification[0].label
            if handedness != "Left":
                continue  # สนใจเฉพาะมือซ้าย

            for idx in FINGER_TIPS:
                lm = handLms.landmark[idx]
                cx, cy = int(lm.x * w), int(lm.y * h)
                s_idx, fret = camera_to_fretboard(cx, cy)
                pressed[idx] = (s_idx, fret)
                print(f"🟡 นิ้ว {FINGER_NAMES[idx]} กดสาย {STRINGS[s_idx]} เฟรต {fret}")

    draw_fretboard(screen, pressed)
    pygame.display.flip()

pipeline.stop()
pygame.quit()
