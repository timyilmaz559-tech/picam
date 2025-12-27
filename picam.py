# picam.py - TAM KOD
import cv2
import struct
import time

cap = cv2.VideoCapture(0)
cap.set(3, 480)
cap.set(4, 320)

def convert_frame(frame):
    height, width = frame.shape[:2]
    fb_data = bytearray()
    for y in range(height):
        for x in range(width):
            b, g, r = frame[y, x]
            pixel = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            fb_data.extend(struct.pack('H', pixel))
    return fb_data

print("Başlatılıyor...")

try:
    fb = open('/dev/fb1', 'wb')
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (480, 320))
        fb_data = convert_frame(frame)
        fb.seek(0)
        fb.write(fb_data)
        cv2.imshow('Kamera', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    fb.close()
except:
    pass

cap.release()
cv2.destroyAllWindows()
