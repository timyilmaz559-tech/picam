#include <DHT.h>
#include <avr/wdt.h>

#define DHTPIN 9
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

const int panel_current_pin = A2;// Panel akım sensörü pini // üretilen enerjinin hesaplanması için kullanılıyor
const int panel_voltage_pin = A0;// Panel voltaj ölçüm pini// üretilen enerjinin hesaplanması için kullanılıyor

const int batarya_enerji_role_pini = 2;// çıkış prizine bataryadan enerji basma/kesme rölesi
const int batarya_panel_sarj_role_pini = 6;// bataryanın panelden şarj kesme rölesi
const int batarya_doluluk_pini = A1;// bataryanın doluluğunu ölçen analog giriş
const int batarya_current_pin = A3;
const int buzzer = 8;

struct datas {
    uint8_t panel_pin_voltage = 0;// panel anlık voltage
    uint8_t panel_pin_last_voltage = 0;// panel anlık son voltage
    float panel_current = 0.0;// Panelin anlık akımı
    float anlik_guc = 0.0;// panelin anlık watt
    float panel_last_current = 0.0;// panelin son anlık akımı

    uint8_t batarya_doluluk_yuzdesi = 0;
    uint8_t batarya_voltage = 0;
    float batarya_current = 0;
    float batary_guc = 0.0;
    float h = 0.00;// nem
    float t = 0.00;// sıcaklık

    // Kullanılan elektrik miktarı için
    float kullanilan_enerji_kwh = 0.0;
    unsigned long son_zaman = 0;

    bool enerji_batarya_kullanimi = false;
    bool batarya_sarj_edilme_durumu = false;
    bool tehlike_durumu = false;// arıza vb. durum bildirim değeri

    char batarya_sarj_gosterim[30] = "";
    char enerji_kullanim_kaynagi[30] = "";
};
datas room;

// state machine time tanımlamaları
unsigned long veri_okuma_sure;
unsigned long sistem_kontrol;
unsigned long veri_gonderme;
unsigned long isi_nem_okuma_sure;

#define VERI_OKUMA_SURE 50
#define SISTEM_KONTROL_SURE 100
#define VERI_GONDERME_SURE 150
#define ISI_NEM_OKUMA_SURE 2000

void setup() {
    // output pins
    pinMode(batarya_enerji_role_pini, OUTPUT);
    pinMode(batarya_panel_sarj_role_pini, OUTPUT);
    pinMode(buzzer, OUTPUT);

    // input pins
    pinMode(batarya_doluluk_pini, INPUT);
    pinMode(batarya_current_pin, INPUT);
    pinMode(panel_current_pin, INPUT);

    // watchdog timer ayarlaması
    wdt_disable();
    delay(100);
    wdt_enable(WDTO_2S);

    Serial.begin(9600);// raspberry ile iletişim portu
    dht.begin();
}

void loop() {
    unsigned long now = millis();
    // watchdog timer kontrolü
    wdt_reset();

    if(now - veri_okuma_sure >= VERI_OKUMA_SURE) {
        veri_okuma();
        veri_okuma_sure = now;
    }

    if(now - isi_nem_okuma_sure >= ISI_NEM_OKUMA_SURE) {
        isi_nem_okuma();
        isi_nem_okuma_sure = now;
    }

    if(now - sistem_kontrol >= SISTEM_KONTROL_SURE) {
        sarj_kontrol();
        guc_cikisi_kontrol();
        ariza_tespit();
        sistem_kontrol = now;
    }

    if(now - veri_gonderme >= VERI_GONDERME_SURE) {
        kullanilan_enerji_hesaplama();
        veri_gonderim();
        veri_gonderme = now;
    }
    
}

void veri_okuma() {
    room.batarya_doluluk_yuzdesi = map(analogRead(batarya_doluluk_pini), 0, 1023, 0, 100);
    room.batarya_voltage = analogRead(batarya_doluluk_pini) / 24;
    int ham_akim = (analogRead(panel_current_pin) / 1023) * 5.0;
    room.batarya_current = (ham_akim - 2.5) / 0.066;

    // Panelin anlık akımını oku (ACS712 30A için)
    int current_raw = analogRead(panel_current_pin);
    float current_voltage = (current_raw / 1023.0) * 5.0;
    room.panel_current = (current_voltage - 2.5) / 0.066;
    
    // panelin voltajını hesapla
    room.panel_pin_voltage = analogRead(panel_voltage_pin) / 24; // Panelden alınan 24V referans
}

void sarj_kontrol() {
    // şarj kontrolü
    if(room.panel_pin_voltage >= 12 && room.batarya_doluluk_yuzdesi < 100) {
        digitalWrite(batarya_panel_sarj_role_pini, HIGH);
        room.batarya_sarj_edilme_durumu = true;
        room.batarya_sarj_gosterim = "Panel";
    }else if(room.batarya_doluluk_yuzdesi < 100 && room.panel_pin_voltage < 12) {
        digitalWrite(batarya_panel_sarj_role_pini, LOW);
        room.batarya_sarj_edilme_durumu = true;
        room.batarya_sarj_gosterim = "Enerji kritik!";
    }else if(room.batarya_doluluk_yuzdesi == 100 && room.panel_pin_voltage >= 12) {
        digitalWrite(batarya_panel_sarj_role_pini, LOW);
        room.batarya_sarj_edilme_durumu = false;
        room.batarya_sarj_gosterim = "Dolu";
    }
}

void guc_cikisi_kontrol() {
    //enerji kullanım kaynağı kontrolü
    if(room.batarya_doluluk_yuzdesi >= 20) {
        digitalWrite(batarya_enerji_role_pini, HIGH);
        room.enerji_kullanim_kaynagi = "Batarya";
    }else if(room.batarya_doluluk_yuzdesi < 20 && room.panel_pin_voltage >= 12 && room.panel_current >= 5) {
        digitalWrite(batarya_enerji_role_pini, LOW);
        room.enerji_kullanim_kaynagi = "Kapalı";
    }else {
        digitalWrite(batarya_enerji_role_pini, LOW);
        room.enerji_kullanim_kaynagi = "Enerji kritik";
    }
}

void kullanilan_enerji_hesaplama() {
    // Kullanılan elektrik miktarı (kWh) hesaplama
    unsigned long simdiki_zaman = millis();
    if(room.enerji_kullanim_kaynagi = "Batarya") {// eğer enerji çıkışı açıksa gücü gerçek hesapla
        room.anlik_guc = room.batarya_voltage * room.batarya_current; // Watt
    }else {// eğer güç çıkışı kapalıysa gücü 0 ata
        room.anlik_guc = 0;
    }
    if (room.son_zaman > 0) {
        float saat_farki = (simdiki_zaman - room.son_zaman) / 3600000.0; // ms -> saat
        room.kullanilan_enerji_kwh += (room.anlik_guc * saat_farki) / 1000.0; // kWh
    }
    room.son_zaman = simdiki_zaman;
}

void isi_nem_okuma() {
    wdt_reset();

    room.h = dht.readHumidity();
    room.t = dht.readTemperature();

    if(isnan(room.h) || isnan(room.t)) {
        return;
    }
}

void veri_gonderim() {
    // Serial üzerinden raspberry'e veri akışı
    Serial.print("K" + String(room.kullanilan_enerji_kwh));
    Serial.print("V" + String(room.panel_pin_voltage));
    Serial.print("PA" + String(room.panel_current));
    Serial.print("T" + String(room.t));
    Serial.print("H" + String(room.h));
    Serial.print("BS" + String(room.batarya_doluluk_yuzdesi));
    Serial.print("T:" + String(room.tehlike_durumu));
}

void ariza_tespit() {
    wdt_reset();
    // olağandışı bir enerji dalgalanması ya da düşüşü ara
    if(room.panel_current < room.panel_last_current && room.panel_last_current - room.panel_current >= 2) {// aradaki fark örnektir
        room.tehlike_durumu = true;
        digitalWrite(buzzer, HIGH);
        delay(250);
        digitalWrite(buzzer, LOW);
        delay(250);
    }else if(room.panel_pin_voltage < room.panel_pin_last_voltage && room.panel_pin_last_voltage - room.panel_pin_voltage >= 10) {// aradaki fark örnektir
        room.tehlike_durumu = true;
        digitalWrite(buzzer, HIGH);
        delay(250);
        digitalWrite(buzzer, LOW);
        delay(250);
    }else {
        room.tehlike_durumu = false;
        digitalWrite(buzzer, LOW);
    }

    // kontrolden sonra son değerleri ata (aynı değer çıkmasını önler)
    room.panel_last_current = room.panel_current;
    room.panel_pin_last_voltage = room.panel_pin_voltage;
}