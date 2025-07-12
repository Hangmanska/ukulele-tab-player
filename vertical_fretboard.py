import pygame
import time
from music21 import converter, pitch

# ---------------- CONFIG ----------------
WIDTH, HEIGHT = 500, 700
FPS = 30
NOTE_DISPLAY_TIME = 1.0  # วินาที

STRINGS = ['G4', 'C4', 'E4', 'A4']  # สาย GCEA
STRING_X = [100, 180, 260, 340]     # ตำแหน่งแนวนอนของแต่ละสาย
FRET_HEIGHT = 50
FRET_COUNT = 10
TOP_MARGIN = 80

# ---------------- FUNCTION: PITCH → STRING/FRET ----------------
def pitch_to_ukulele_fret(note_name):
    npitch = pitch.Pitch(note_name)
    for s_idx, open_str in enumerate(STRINGS):
        base = pitch.Pitch(open_str)
        fret = npitch.midi - base.midi
        if 0 <= fret <= FRET_COUNT:
            return s_idx, fret
    return None, None

# ---------------- PARSE MUSICXML ----------------
score = converter.parse("cyclone_tab.xml")
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
pygame.display.set_caption("Ukulele Vertical Fretboard Viewer")
font = pygame.font.SysFont("Arial", 24)
clock = pygame.time.Clock()

# ---------------- MAIN LOOP ----------------
start_time = time.time()
running = True

while running:
    screen.fill((10, 10, 10))
    current_time = time.time() - start_time
    current_beat = current_time * 2  # สมมุติ 120 BPM

    # วาดสายแนวตั้ง
    for i, x in enumerate(STRING_X):
        pygame.draw.line(screen, (220, 220, 220), (x, TOP_MARGIN), (x, TOP_MARGIN + FRET_COUNT * FRET_HEIGHT), 2)
        label = font.render(STRINGS[i][0], True, (255, 255, 255))
        screen.blit(label, (x - label.get_width() // 2, 30))

    # วาดเส้นเฟรตแนวนอน
    for fret in range(FRET_COUNT + 1):
        y = TOP_MARGIN + fret * FRET_HEIGHT
        pygame.draw.line(screen, (100, 100, 100), (STRING_X[0] - 40, y), (STRING_X[-1] + 40, y), 1)

        # ตัวเลขเฟรต
        if fret > 0:
            num_label = font.render(str(fret), True, (150, 150, 150))
            screen.blit(num_label, (STRING_X[-1] + 50, y - FRET_HEIGHT // 2))

    # วาดโน้ตปัจจุบัน
    for note in note_schedule:
        if abs(note["time"] - current_beat) < NOTE_DISPLAY_TIME:
            x = STRING_X[note["string"]]
            y = TOP_MARGIN + note["fret"] * FRET_HEIGHT
            pygame.draw.circle(screen, (255, 255, 0), (x, y), 18)
            text = font.render(str(note["fret"]), True, (0, 0, 0))
            screen.blit(text, (x - text.get_width() // 2, y - text.get_height() // 2))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
