
import numpy as np

# พิกัด X ที่คาลิเบรตแล้วของสาย G C E A
STRING_X_CALIB = [120, 180, 250, 310]  # ค่าตัวอย่าง ต้องปรับตามตำแหน่งจริงของกล้อง

# พิกัด Y ที่คาลิเบรตแล้วของเฟรต 0 ถึง 10
FRET_Y_CALIB = [100, 130, 160, 190, 220, 250, 280, 310, 340, 370, 400]

def camera_to_fretboard(cx, cy):
    """
    แปลงพิกัดกล้อง (cx, cy) ไปยังตำแหน่งสาย (0–3) และเฟรต (0–10)
    """
    string_idx = None
    for i in range(len(STRING_X_CALIB)-1):
        mid = (STRING_X_CALIB[i] + STRING_X_CALIB[i+1]) / 2
        if cx < mid:
            string_idx = i
            break
    if string_idx is None and cx >= STRING_X_CALIB[-1]:
        string_idx = len(STRING_X_CALIB) - 1

    fret_idx = None
    for i in range(len(FRET_Y_CALIB)-1):
        mid = (FRET_Y_CALIB[i] + FRET_Y_CALIB[i+1]) / 2
        if cy < mid:
            fret_idx = i
            break
    if fret_idx is None and cy >= FRET_Y_CALIB[-1]:
        fret_idx = len(FRET_Y_CALIB) - 1

    if string_idx is None or fret_idx is None:
        return None, None

    return string_idx, fret_idx
