# kamera_only.py
from flask import Flask, Response
from picamera2 import Picamera2
import time

app = Flask(__name__)

# Kamera
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()

time.sleep(2)  # Kamera ısınması

def generate():
    while True:
        frame = picam2.capture_array()
        
        # JPEG'e çevir (basit)
        import cv2
        ret, jpeg = cv2.imencode('.jpg', frame)
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + 
               jpeg.tobytes() + b'\r\n')
        
        time.sleep(0.033)

@app.route('/')
def index():
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
