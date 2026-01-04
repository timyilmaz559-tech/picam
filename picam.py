import cv2
import numpy as np
import os

# fb0 (framebuffer) ayarları
fb_width = 480   # SPI ekran genişliği
fb_height = 320  # SPI ekran yüksekliği
fb_path = "/dev/fb0"

# Kamera ayarları
camera_width = 640
camera_height = 480

def write_to_framebuffer(frame):
    """Görüntüyü framebuffer'a yaz"""
    try:
        # SPI ekran boyutuna yeniden boyutlandır
        resized_frame = cv2.resize(frame, (fb_width, fb_height))
        
        # BGR'den RGB'ye çevir (SPI ekranlar genelde RGB kullanır)
        rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        
        # Framebuffer'ı aç ve yaz
        with open(fb_path, 'wb') as fb:
            # Görüntü verisini yaz
            fb.write(rgb_frame.tobytes())
            
    except Exception as e:
        print(f"Framebuffer yazma hatası: {e}")

def main():
    # Kamera başlatma (Picamera için)
    try:
        # Picamera2 kullanımı (Raspberry Pi OS Bullseye ve sonrası)
        try:
            from picamera2 import Picamera2
            picam2 = Picamera2()
            config = picam2.create_preview_configuration(
                main={"size": (camera_width, camera_height)}
            )
            picam2.configure(config)
            picam2.start()
            use_picamera2 = True
            print("Picamera2 başlatıldı")
        except:
            # Eski Picamera kullanımı
            import picamera
            import picamera.array
            camera = picamera.PiCamera()
            camera.resolution = (camera_width, camera_height)
            use_picamera2 = False
            print("Eski Picamera başlatıldı")
            
    except ImportError:
        print("Picamera bulunamadı, USB kamera kullanılıyor...")
        # USB kamera kullan
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, camera_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_height)
        use_picamera2 = None
        print("USB kamera başlatıldı")
    
    print("Kamera görüntüsü SPI ekrana aktarılıyor...")
    print("Çıkmak için CTRL+C tuşlarına basın")
    
    try:
        while True:
            if use_picamera2 is True:
                # Picamera2 kullan
                frame = picam2.capture_array()
                # Picamera2 BGR formatında verir
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                
            elif use_picamera2 is False:
                # Eski Picamera kullan
                with picamera.array.PiRGBArray(camera) as stream:
                    camera.capture(stream, format='bgr')
                    frame = stream.array
            else:
                # USB kamera kullan
                ret, frame = cap.read()
                if not ret:
                    break
            
            # Görüntüyü framebuffer'a yaz
            write_to_framebuffer(frame)
            
    except KeyboardInterrupt:
        print("\nProgram sonlandırılıyor...")
    finally:
        # Kaynakları serbest bırak
        if use_picamera2 is True:
            picam2.stop()
        elif use_picamera2 is False:
            camera.close()
        else:
            cap.release()
        print("Kamera kapatıldı")

if __name__ == "__main__":
    main()
