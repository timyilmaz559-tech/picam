from picamera2 import Picamera2
import cv2
import numpy as np

FB_PATH = "/dev/fb0"
SCREEN_W = 480
SCREEN_H = 320

def main():
    try:
        picam2 = Picamera2()
        picam2.configure(picam2.create_preview_configuration())
        picam2.start()
        print("CSI Kamera başlatıldı")
    except:
        print("CSI kamera bulunamadı, USB deneniyor...")
        return
    
    try:
        while True:
            frame = picam2.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            small = cv2.resize(frame, (SCREEN_W, SCREEN_H))
            rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
            
            with open(FB_PATH, 'wb') as fb:
                fb.write(rgb.tobytes())
                
    except KeyboardInterrupt:
        print("\nDurduruldu")
    finally:
        picam2.stop()

if __name__ == "__main__":
    main()
