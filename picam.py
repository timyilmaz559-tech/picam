# simple_spi_camera.py
import cv2
import struct
import time

print("Başlatılıyor...")

# Kamera
cap = cv2.VideoCapture(0)
cap.set(3, 480)
cap.set(4, 320)

# FrameBuffer
fb = open('/dev/fb1', 'wb')

try:
    while True:
        # Frame oku
        ret, frame = cap.read()
        if not ret:
            continue
        
        # 480x320'e resize et
        frame = cv2.resize(frame, (480, 320))
        
        # RGB565'e çevir ve yaz
        fb.seek(0)
        for y in range(320):
            for x in range(480):
                b, g, r = frame[y, x]
                pixel = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
                fb.write(struct.pack('H', pixel))
        
        # Konsola durum yaz (her 60 framede bir)
        if int(time.time()) % 2 == 0:  # 2 saniyede bir
            print(f"SPI ekrana yazılıyor... {time.strftime('%H:%M:%S')}")
        
        time.sleep(0.033)
        
except KeyboardInterrupt:
    print("\nDurduruldu.")
finally:
    cap.release()
    fb.close()
    print("Temizlik yapıldı.")
