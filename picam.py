# kamera_picamera2.py
from picamera2 import Picamera2
import time
import struct

print("Picamera2 başlatılıyor...")

# 1. Picamera2'yi başlat
picam2 = Picamera2()

# 2. Konfigürasyon
config = picam2.create_preview_configuration(
    main={"size": (480, 320), "format": "RGB888"}
)
picam2.configure(config)

# 3. Başlat
picam2.start()
time.sleep(2)  # Kamera ısınması için

print("Kamera hazır! SPI ekrana yazılıyor...")

try:
    with open('/dev/fb1', 'wb') as fb:
        frame_count = 0
        
        while True:
            # Frame yakala (VideoCapture yerine)
            frame = picam2.capture_array()
            
            # SPI ekrana yaz
            fb.seek(0)
            for y in range(320):
                for x in range(480):
                    r, g, b = frame[y, x]
                    # RGB565 formatına çevir
                    pixel = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                    fb.write(struct.pack('H', pixel))
            
            # Ekrana durum yaz
            frame_count += 1
            if frame_count % 30 == 0:
                print(f"Frame: {frame_count}")
            
            # FPS kontrolü
            time.sleep(0.033)  # ~30 FPS
                
except KeyboardInterrupt:
    print("\nDurduruldu.")
finally:
    picam2.stop()
    print("Kamera durduruldu.")
