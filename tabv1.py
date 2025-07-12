import pygame
import time
from music21 import converter, pitch

# ---------------- CONFIG ----------------
WIDTH, HEIGHT = 800, 400
FPS = 30
NOTE_DISPLAY_TIME = 1.0  # วินาที
STRINGS = ['G4', 'C4', 'E4', 'A4']  # ตั้งสายมาตรฐานของ Ukulele
STRING_Y = [80, 140, 200, 260]
FRET_WIDTH = 60
MAX_FRET = 5

# ---------------- FUNCTION: PITCH → STRING/FRET ----------------
def pitch_to_ukulele_fret(note_name):
    npitch = pitch.Pitch(note_name)
    for s_idx, open_str in enumerate(STRINGS):
        base = pitch.Pitch(open_str)
        fret = npitch.midi - base.midi
        if 0 <= fret <= MAX_FRET:
            return s_idx, fret
    return None, None

# ---------------- PARSE MUSICXML ----------------
score = converter.parse("intro_jumtamai.xml")
notes = score.parts[0].flat.notes

note_schedule = []
for note in notes:
    if note.isNote:
        string_idx, fret = pitch_to_ukulele_fret(note.pitch.nameWithOctave)
        if string_idx is not None:
            note_schedule.append({
                "time": float(note.offset),
                "duration": float(note.quarterLength),
                "string": string_idx,
                "fret": fret
            })

# ---------------- INIT PYGAME ----------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ukulele Fretboard Viewer")
font = pygame.font.SysFont("Arial", 28)
clock = pygame.time.Clock()

# ---------------- MAIN LOOP ----------------
start_time = time.time()
running = True

while running:
    screen.fill((10, 10, 10))
    current_time = time.time() - start_time
    current_beat = current_time * 2  # สมมุติ 120 BPM

    # วาดสาย
    for i, y in enumerate(STRING_Y):
        pygame.draw.line(screen, (200, 200, 200), (50, y), (WIDTH - 50, y), 2)
        for fret in range(MAX_FRET + 1):
            x = 100 + fret * FRET_WIDTH
            pygame.draw.line(screen, (50, 50, 50), (x, y - 20), (x, y + 20), 1)

             # เพิ่มชื่อสายด้านซ้าย
            label = font.render(STRINGS[i][0], True, (255, 255, 255))  # แสดงตัวแรกของ G4, C4, ...
            screen.blit(label, (20, y - label.get_height() // 2))

    # วาดโน้ตที่เล่นในขณะนี้
    for note in note_schedule:
        if abs(note["time"] - current_beat) < NOTE_DISPLAY_TIME:
            x = 100 + note["fret"] * FRET_WIDTH
            y = STRING_Y[note["string"]]
            pygame.draw.circle(screen, (255, 255, 0), (x, y), 15)
            text = font.render(str(note["fret"]), True, (0, 0, 0))
            screen.blit(text, (x - text.get_width() // 2, y - text.get_height() // 2))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
