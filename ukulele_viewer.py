import pygame
import time
from music21 import converter, pitch

# ---------------- CONFIG ----------------
WIDTH, HEIGHT = 500, 700
FPS = 30
NOTE_DISPLAY_TIME = 1.0  # วินาทีที่แสดงโน้ต

STRINGS = ['G4', 'C4', 'E4', 'A4']  # สายบนสุด -> ล่างสุด
FRET_COUNT = 10
FRET_HEIGHT = 50
TOP_MARGIN = 100

# สร้างตำแหน่งสาย (แนวแกน X) ให้กระจายอัตโนมัติ
STRING_X = [int(WIDTH * (i + 1) / (len(STRINGS) + 1)) for i in range(len(STRINGS))]

# ---------------- HELPER ----------------
def pitch_to_ukulele_fret(note_name):
    npitch = pitch.Pitch(note_name)
    for s_idx, open_str in enumerate(STRINGS):
        base = pitch.Pitch(open_str)
        fret = npitch.midi - base.midi
        if 0 <= fret <= FRET_COUNT:
            return s_idx, fret
    return None, None

# ---------------- LOAD TAB ----------------
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

is_playing = True
playback_speed = 1.0
start_time = time.time()

# ---------------- UI DRAW ----------------
def draw_ui(screen, font, is_playing, playback_speed):
    # ปุ่ม play/pause
    pygame.draw.rect(screen, (40, 40, 40), (20, 20, 50, 40))
    symbol = "▶" if not is_playing else "❚❚"
    label = font.render(symbol, True, (255, 255, 255))
    screen.blit(label, (30, 25))

    # ชื่อสาย (G C E A)
    for i, x in enumerate(STRING_X):
        s_label = font.render(STRINGS[i][0], True, (255, 255, 255))
        screen.blit(s_label, (x - s_label.get_width() // 2, TOP_MARGIN - 30))

    # ตัวเลขความเร็ว + slider
    speed_label = font.render(f"{playback_speed:.2f}x", True, (255, 255, 255))
    screen.blit(speed_label, (20, HEIGHT - 40))
    slider_x = 120
    slider_y = HEIGHT - 30
    pygame.draw.rect(screen, (80, 80, 80), (slider_x, slider_y, 200, 5))
    knob_x = int(slider_x + (playback_speed - 0.25) / (2.0 - 0.25) * 200)
    pygame.draw.circle(screen, (255, 255, 0), (knob_x, slider_y + 3), 8)

# ---------------- MAIN LOOP ----------------
running = True
while running:
    screen.fill((10, 10, 10))

    if is_playing:
        current_time = time.time() - start_time
    else:
        current_time = current_time if 'current_time' in locals() else 0
    current_beat = current_time * 2 * playback_speed  # assuming 120 bpm

    # วาดสาย
    for x in STRING_X:
        pygame.draw.line(screen, (220, 220, 220), (x, TOP_MARGIN), (x, TOP_MARGIN + FRET_COUNT * FRET_HEIGHT), 2)

    # วาดเฟรต
    for fret in range(FRET_COUNT + 1):
        y = TOP_MARGIN + fret * FRET_HEIGHT
        pygame.draw.line(screen, (100, 100, 100), (STRING_X[0] - 40, y), (STRING_X[-1] + 40, y), 1)
        if fret > 0:
            num_label = font.render(str(fret), True, (150, 150, 150))
            screen.blit(num_label, (STRING_X[-1] + 50, y - FRET_HEIGHT // 2))

    # วาดโน้ต
    for note in note_schedule:
        if abs(note["time"] - current_beat) < NOTE_DISPLAY_TIME:
            x = STRING_X[note["string"]]
            y = TOP_MARGIN + note["fret"] * FRET_HEIGHT
            pygame.draw.circle(screen, (255, 255, 0), (x, y), 18)
            text = font.render(str(note["fret"]), True, (0, 0, 0))
            screen.blit(text, (x - text.get_width() // 2, y - text.get_height() // 2))

    draw_ui(screen, font, is_playing, playback_speed)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            # ปุ่ม play/pause
            if 20 <= mx <= 70 and 20 <= my <= 60:
                is_playing = not is_playing
                if is_playing:
                    start_time = time.time() - current_time
            # slider
            elif 120 <= mx <= 320 and HEIGHT - 35 <= my <= HEIGHT - 25:
                relative_x = mx - 120
                playback_speed = 0.25 + (relative_x / 200) * (2.0 - 0.25)
                playback_speed = round(playback_speed, 2)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
