from music21 import converter, pitch
import matplotlib.pyplot as plt

# ---------- CONFIG ----------
MUSICXML_PATH = "cyclone_tab.xml"
BPM = 80  # ปรับตามเพลงจริง ถ้าไม่แน่ใจใช้ 80-100
show_debug = True  # ปริ้นท์ข้อมูลโน้ต

# ---------- LOAD XML ----------
score = converter.parse(MUSICXML_PATH)
notes = score.parts[0].flat.notes

note_schedule = []

for note in notes:
    if note.isNote:
        info = {
            "pitch": note.pitch.nameWithOctave,
            "offset": float(note.offset),
            "duration": float(note.quarterLength),
        }
        note_schedule.append(info)

# ---------- คำนวณเวลา ----------
total_beats = max(n["offset"] + n["duration"] for n in note_schedule)
total_seconds = total_beats * (60.0 / BPM)

print("🎵 จำนวนโน้ตทั้งหมด:", len(note_schedule))
print("🕓 ยาวสุดถึง beat:", round(total_beats, 2))
print(f"⏱️ ใช้เวลาเล่นทั้งหมดประมาณ: {total_seconds:.2f} วินาที (ที่ {BPM} BPM)")

if show_debug:
    print("\n🔍 รายละเอียดโน้ต:")
    for n in note_schedule[:10]:  # โชว์แค่ 10 ตัวอย่างแรก
        print(f" - {n['pitch']:4s} @ beat {n['offset']:>5.2f}  (len {n['duration']})")

# ---------- วาดกราฟ timeline ----------
times = [n["offset"] for n in note_schedule]
durations = [n["duration"] for n in note_schedule]
pitches = [n["pitch"] for n in note_schedule]

plt.figure(figsize=(12, 4))
plt.bar(times, durations, width=0.1, color='skyblue', edgecolor='black')
plt.xlabel("Beat")
plt.ylabel("Duration")
plt.title(f"🎵 Timeline of '{MUSICXML_PATH}' ({len(note_schedule)} notes @ {BPM} BPM)")
plt.grid(True, linestyle='--', alpha=0.3)
plt.tight_layout()
plt.show()
