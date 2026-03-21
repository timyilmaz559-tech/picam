from picamera2 import Picamera2
import cv2
import numpy as np
import socket
import time

# Kamera başlat
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration())
picam2.start()

# Basit HTTP yanıtı
HTML = """HTTP/1.1 200 OK
Content-Type: multipart/x-mixed-replace; boundary=frame

"""

# Socket oluştur
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('0.0.0.0', 8080))
server.listen(1)

print("🌐 http://[RASPBERRY_IP]:8080 adresinden izleyebilirsiniz")

while True:
    client, addr = server.accept()
    print(f"İstemci bağlandı: {addr}")
    client.send(HTML.encode())
    
    try:
        while True:
            # Kare yakala
            frame = picam2.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # JPEG'e çevir
            ret, jpeg = cv2.imencode('.jpg', frame)
            
            # HTTP frame olarak gönder
            client.send(b'--frame\r\n')
            client.send(b'Content-Type: image/jpeg\r\n\r\n')
            client.send(jpeg.tobytes())
            client.send(b'\r\n')
            
            time.sleep(0.05)  # 20 FPS
            
    except:
        client.close()
