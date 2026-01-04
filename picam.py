import cv2
import numpy as np

# SPI ekran ayarları
FB_PATH = "/dev/fb0"
SCREEN_W = 480
SCREEN_H = 320

# Kamera ayarları
CAM_W = 640
CAM_H = 480

def main():
    # USB kamera başlat
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_H)
    
    print("Kamera başlatıldı. Çıkmak için CTRL+C")
    
    try:
        while True:
            # Frame oku
            ret, frame = cap.read()
            if not ret:
                break
            
            # SPI ekran boyutuna küçült
            small = cv2.resize(frame, (SCREEN_W, SCREEN_H))
            
            # BGR -> RGB çevir (SPI ekran için)
            rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
            
            # SPI ekrana yaz
            with open(FB_PATH, 'wb') as fb:
                fb.write(rgb.tobytes())
                
    except KeyboardInterrupt:
        print("\nProgram durduruldu")
    finally:
        cap.release()

if __name__ == "__main__":
    main()
