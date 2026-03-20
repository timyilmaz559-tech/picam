#include <WiFi.h>
#include <Adafruit_GFX.h> // grafik kütüphanesi
#include <Adafruit_ST7735.h> // donanım kütüphanesi
#include <SPI.h>

// ev ağı bilgileri
const char* ssid="Cennet571";
const char* pss="571cennet571";

// 1.8 tft lcd ekran
int sclk = 13;
int mosi = 11;
int cs = 10;
int dc = 9;
int rst = 8;
Adafruit_ST7735 tft = Adafruit_ST7735 (cs, dc, rst);

const int sound_level_sensor = 12;
const int buzzer = 13;

int sound_level = 0;

// state machine tanımlamaları
unsigned long start_time = 0;

#define TOTAL_TIME 100

void setup() {
  Serial.begin(9600);

  pinMode(sound_level_sensor, INPUT);
  pinMode(buzzer, OUTPUT);

  int tries = 0;
  Wifi.begin(ssid, pss);
  while(Wifi.status() != WL_CONNECTED && tries < 20) {
    Serial.print(".");
    tries++;
    delay(1000);
  }
  Wifi.mode(WIFI_AP_STA);

  tft.initR(INITR_BLACKTAB);
}

void loop() {
  unsigned long now = millis();

  if(now - start_time >= TOTAL_TIME) {
    sensor_read();
    display_update();
    start_time = now;
  }
}

void sensor_read() {
  sound_level = map(analogRead(sound_level_sensor), 0, 1023, 0, 100);
  if(sound_level >= 40) {
    digitalWrite(buzzer, HIGH);
    delay(100);
    digitalWrite(buzzer, LOW);
    delay(100);
  }else {
    digitalWrite(buzzer, LOW);
  }
}

void display_update() {
  tft.fillScreen (ST7735_BLACK);
  tft.setTextColor(ST7735_RED);
  tft.setTextSize(1);
  tft.setCursor (5, 5);
  tft.print("WIFI_CON_IP: ");
  tft.println(Wifi.localIP());
  tft.print("WIFI_CON_STATE: ");
  tft.println(Wifi.status());
  tft.print("SOUND: ");
  tft.println(sound_level + "dB");
}