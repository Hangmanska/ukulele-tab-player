
import pygame
import time
from music21 import converter

# ---------------- CONFIG ----------------
WIDTH, HEIGHT = 800, 600
FPS = 30
NOTE_DISPLAY_TIME = 1.5  # วินาที

# ---------------- MUSIC PARSING ----------------
score = converter.parse("intro_jumtamai.xml")  # ต้องอยู่ในโฟลเดอร์เดียวกัน
notes = score.parts[0].flat.notes

note_schedule = []
for note in notes:
    if note.isNote:
        note_schedule.append({
            "pitch": note.pitch.nameWithOctave,
            "time": float(note.offset),
            "duration": float(note.quarterLength)
        })

# ---------------- INIT PYGAME ----------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ukulele Play-Along Tab Viewer")
font = pygame.font.SysFont("Arial", 48)
clock = pygame.time.Clock()

# ---------------- MAIN LOOP ----------------
start_time = time.time()
running = True

while running:
    screen.fill((30, 30, 30))
    current_time = time.time() - start_time  # วินาที
    current_beat = current_time * 2  # สมมุติ 120 BPM → 2 beats/sec

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # หาโน้ตที่ควรแสดงในตอนนี้
    for note in note_schedule:
        if abs(note["time"] - current_beat) < NOTE_DISPLAY_TIME:
            text = font.render(note["pitch"], True, (255, 255, 0))
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
