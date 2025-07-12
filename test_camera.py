﻿
import cv2
import pyrealsense2 as rs
import numpy as np

pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

print("📷 เริ่มต้นทดสอบกล้อง RealSense")

try:
    while True:
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            print("❌ ไม่พบภาพจากกล้อง")
            continue
        frame = np.asanyarray(color_frame.get_data())
        cv2.imshow("RealSense Camera", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break
finally:
    pipeline.stop()
    cv2.destroyAllWindows()
