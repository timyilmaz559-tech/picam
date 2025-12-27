import cv2
import struct
import time

cap = cv2.VideoCapture(0)

cap.set(3, 480)
cap.set(4, 320)
ret, frame = cap.read()

def convert_frame(frame):
  height, width = frame.shape[:2]
  fb_data = bytearray()

for y in range(height):
        for x in range(width):
            b, g, r = frame[y, x]  # OpenCV BGR formatı
            # RGB565'e çevir
            pixel = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            fb_data.extend(struct.pack('H', pixel))
    
    return fb_data

with open('/dev/fb1', 'wb') as fb:
    while True:
        ret, frame = camera.read()
        if not ret:
            break
        
      # Frame'i SPI ekran boyutuna getir
      frame = cv2.resize(frame, (480, 320))
        
      # Dönüştür ve yaz
      fb_data = convert_frame(frame)
      fb.seek(0)
      fb.write(fb_data)

      cv2.imshow('kamera', frame)
      if cv2.waitkey(1) & 0xFF == ord('q')
        break
        
      # FPS sınırla
      time.sleep(0.033)  # ~30 FPS

cv2.imshow('kamera', frame)

cap.release()
cv2.destroyAllWindows()
