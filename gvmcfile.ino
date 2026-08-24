// ============================================================
//  RTC BUS PASS VALIDATOR — Serial Monitor Version
//  Hardware : ESP32 + RC522 RFID + 16x2 LCD (I2C)
//  LEDs     : NOT required — results shown in Serial Monitor
// ============================================================

#include <SPI.h>
#include <MFRC522.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ── Pin definitions ──────────────────────────────────────────
#define RFID_SS_PIN   5
#define RFID_RST_PIN  4
#define BUZZER_PIN    14   // optional — comment out if no buzzer

// ── WiFi credentials ─────────────────────────────────────────
const char* WIFI_SSID     = "OPPO A17";
const char* WIFI_PASSWORD = "1234567789";

// ── Firebase config ──────────────────────────────────────────
const char* FIREBASE_PROJECT_ID = "rtc-bus-tracker-1e232";
const char* FIREBASE_API_KEY    = "AIzaSyBDJX7Ls-SwrNdb-X9soA4HEyrw3cGsvLs";
const char* DEVICE_EMAIL        = "ilovemyselfonly320@gmail.com";
const char* DEVICE_PASSWORD     = "Bhanu@420";

// ── Objects ──────────────────────────────────────────────────
MFRC522 rfid(RFID_SS_PIN, RFID_RST_PIN);
LiquidCrystal_I2C lcd(0x27, 16, 2);

// ── State ─────────────────────────────────────────────────────
String idToken    = "";
unsigned long tokenExpiry = 0;
String lastCardUID  = "";
unsigned long lastTapTime = 0;
const unsigned long DEBOUNCE_MS = 3000;

// ============================================================
void setup() {
  Serial.begin(115200);
  delay(500);

  // NO LED pinMode needed

  // Buzzer (optional)
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  printBanner();

  lcd.init();
  lcd.backlight();
  lcdPrint("RTC Bus Pass", "Initialising..");

  SPI.begin();
  rfid.PCD_Init();

  connectWiFi();
  configTime(5 * 3600 + 30 * 60, 0, "pool.ntp.org");  // IST +5:30

  Serial.println("⏳ Syncing time with NTP...");
  struct tm timeinfo;
  int attempts = 0;
  while (!getLocalTime(&timeinfo) && attempts < 10) {
    delay(500); attempts++;
  }
  if (getLocalTime(&timeinfo)) {
    char buf[32];
    strftime(buf, sizeof(buf), "%d-%m-%Y %H:%M:%S", &timeinfo);
    Serial.println("✅ Time synced: " + String(buf));
  } else {
    Serial.println("⚠️  NTP sync failed — expiry check may be inaccurate");
  }

  authenticateDevice();

  lcdPrint("Place your card", "   on reader...");
  Serial.println("\n📟 Ready — tap a card on the reader\n");
  printDivider();
}

// ============================================================
void loop() {
  if (millis() > tokenExpiry) {
    Serial.println("🔄 Token expired — re-authenticating...");
    authenticateDevice();
  }

  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) {
    return;
  }

  String uid = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    if (rfid.uid.uidByte[i] < 0x10) uid += "0";
    uid += String(rfid.uid.uidByte[i], HEX);
  }
  uid.toUpperCase();

  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();

  if (uid == lastCardUID && (millis() - lastTapTime) < DEBOUNCE_MS) {
    return; // silent debounce
  }
  lastCardUID = uid;
  lastTapTime = millis();

  printDivider();
  Serial.println("🃏 CARD DETECTED");
  Serial.println("   UID : " + uid);

  struct tm t;
  if (getLocalTime(&t)) {
    char buf[32];
    strftime(buf, sizeof(buf), "%d-%m-%Y %H:%M:%S", &t);
    Serial.println("   Time: " + String(buf));
  }

  lcdPrint("Checking...", uid);
  validateCard(uid);
}

// ============================================================
void connectWiFi() {
  Serial.print("📶 Connecting to WiFi: ");
  Serial.println(WIFI_SSID);
  lcdPrint("Connecting WiFi", WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi connected!");
    Serial.println("   IP : " + WiFi.localIP().toString());
    lcdPrint("WiFi Connected!", WiFi.localIP().toString());
    delay(1200);
  } else {
    Serial.println("\n❌ WiFi FAILED — check SSID/password");
    lcdPrint("WiFi Failed!", "Check settings");
    while (true) { delay(1000); } // halt
  }
}

// ============================================================
void authenticateDevice() {
  Serial.println("🔐 Authenticating with Firebase...");
  lcdPrint("Authenticating", "Firebase...");

  HTTPClient http;
  String url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=";
  url += FIREBASE_API_KEY;

  http.begin(url);
  http.addHeader("Content-Type", "application/json");

  String body = "{\"email\":\"" + String(DEVICE_EMAIL) +
                "\",\"password\":\"" + String(DEVICE_PASSWORD) +
                "\",\"returnSecureToken\":true}";

  int code = http.POST(body);

  if (code == 200) {
    DynamicJsonDocument doc(2048);
    deserializeJson(doc, http.getString());
    idToken      = doc["idToken"].as<String>();
    tokenExpiry  = millis() + (3540UL * 1000UL);
    Serial.println("✅ Firebase auth successful");
    lcdPrint("Place your card", "   on reader...");
  } else {
    Serial.println("❌ Firebase auth FAILED");
    Serial.println("   Code   : " + String(code));
    Serial.println("   Reason : " + http.getString());
    lcdPrint("Auth Failed!", "Check API key");
    delay(3000);
  }
  http.end();
}

// ============================================================
void validateCard(String uid) {
  if (WiFi.status() != WL_CONNECTED) connectWiFi();

  Serial.println("\n🔍 Querying Firestore...");

  HTTPClient http;
  String url = "https://firestore.googleapis.com/v1/projects/";
  url += FIREBASE_PROJECT_ID;
  url += "/databases/(default)/documents/passengers/";
  url += uid;

  http.begin(url);
  http.addHeader("Authorization", "Bearer " + idToken);
  http.addHeader("Content-Type", "application/json");

  int code = http.GET();
  String payload = http.getString();
  http.end();

  Serial.println("   HTTP code: " + String(code));

  // ── Card not in database ──
  if (code == 404) {
    showInvalid(uid, "NOT REGISTERED", "This card UID is not in the database.");
    return;
  }

  // ── Server / network error ──
  if (code != 200) {
    Serial.println("❌ Firestore error: " + payload);
    showInvalid(uid, "SERVER ERROR " + String(code), "Check Firebase console.");
    return;
  }

  // ── Card found — parse document ──
  DynamicJsonDocument doc(4096);
  DeserializationError err = deserializeJson(doc, payload);
  if (err) {
    showInvalid(uid, "PARSE ERROR", String(err.c_str()));
    return;
  }

  JsonObject fields = doc["fields"];

  String name      = getField(fields, "name");
  String passType  = getField(fields, "passType");
  String route     = getField(fields, "route");
  String phone     = getField(fields, "phone");
  String validUntil = getExpiry(fields);

  bool valid = isPassValid(fields);

  // ── Print full result to Serial Monitor ──
  Serial.println();
  Serial.println("┌─────────────────────────────────┐");
  if (valid) {
    Serial.println("│         ✅  PASS VALID           │");
  } else {
    Serial.println("│         ❌  PASS INVALID         │");
  }
  Serial.println("├─────────────────────────────────┤");
  Serial.println("│ Card UID   : " + padRight(uid, 19) + "│");
  Serial.println("│ Name       : " + padRight(name, 19) + "│");
  Serial.println("│ Phone      : " + padRight(phone, 19) + "│");
  Serial.println("│ Pass Type  : " + padRight(passType, 19) + "│");
  Serial.println("│ Route      : " + padRight(route, 19) + "│");
  Serial.println("│ Valid Until: " + padRight(validUntil, 19) + "│");
  Serial.println("└─────────────────────────────────┘");

  if (valid) {
    // ── VALID ──
    lcdPrint("VALID  :)", name.length() > 16 ? name.substring(0,16) : name);
    // Single beep (comment out if no buzzer)
    tone(BUZZER_PIN, 1000, 150);
    delay(2500);
    // Show pass details
    String line2 = passType + " | " + route;
    lcdPrint(name.length() > 16 ? name.substring(0,16) : name,
             line2.length() > 16 ? line2.substring(0,16) : line2);
    delay(2000);
    logTapEvent(uid, true);

  } else {
    // ── INVALID ──
    lcdPrint("INVALID :(", "Pass Expired!");
    // Three beeps (comment out if no buzzer)
    for (int i = 0; i < 3; i++) { tone(BUZZER_PIN, 400, 200); delay(300); }
    delay(3000);
    logTapEvent(uid, false);
  }

  lcdPrint("Place your card", "   on reader...");
  printDivider();
}

// ============================================================
void showInvalid(String uid, String reason, String detail) {
  Serial.println();
  Serial.println("┌─────────────────────────────────┐");
  Serial.println("│         ❌  PASS INVALID         │");
  Serial.println("├─────────────────────────────────┤");
  Serial.println("│ Card UID : " + padRight(uid, 21) + "│");
  Serial.println("│ Reason   : " + padRight(reason, 21) + "│");
  Serial.println("│ Detail   : " + padRight(detail, 21) + "│");
  Serial.println("└─────────────────────────────────┘");
  lcdPrint("INVALID :(", reason.length() > 16 ? reason.substring(0,16) : reason);
  for (int i = 0; i < 3; i++) { tone(BUZZER_PIN, 400, 200); delay(300); }
  delay(3000);
  lcdPrint("Place your card", "   on reader...");
  printDivider();
}

// ============================================================
String getField(JsonObject& fields, const char* key) {
  if (!fields.containsKey(key)) return "N/A";
  JsonObject f = fields[key];
  if (f.containsKey("stringValue"))    return f["stringValue"].as<String>();
  if (f.containsKey("integerValue"))   return f["integerValue"].as<String>();
  if (f.containsKey("timestampValue")) return f["timestampValue"].as<String>();
  return "N/A";
}

// Returns formatted expiry date "DD-MM-YYYY"
String getExpiry(JsonObject& fields) {
  if (!fields.containsKey("validUntil")) return "N/A";
  JsonObject f = fields["validUntil"];
  String ts = "";
  if (f.containsKey("timestampValue")) ts = f["timestampValue"].as<String>();
  else if (f.containsKey("stringValue")) ts = f["stringValue"].as<String>();
  if (ts.length() < 10) return "N/A";
  // Convert "YYYY-MM-DD..." → "DD-MM-YYYY"
  return ts.substring(8,10) + "-" + ts.substring(5,7) + "-" + ts.substring(0,4);
}

// ============================================================
bool isPassValid(JsonObject& fields) {
  if (!fields.containsKey("validUntil")) return false;
  JsonObject f = fields["validUntil"];
  String ts = "";
  if (f.containsKey("timestampValue")) ts = f["timestampValue"].as<String>();
  else if (f.containsKey("stringValue")) ts = f["stringValue"].as<String>();
  if (ts.length() < 10) return false;

  int expYear  = ts.substring(0, 4).toInt();
  int expMonth = ts.substring(5, 7).toInt();
  int expDay   = ts.substring(8, 10).toInt();

  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) return true; // assume valid if no time

  int curYear  = timeinfo.tm_year + 1900;
  int curMonth = timeinfo.tm_mon + 1;
  int curDay   = timeinfo.tm_mday;

  if (curYear  < expYear)  return true;
  if (curYear  > expYear)  return false;
  if (curMonth < expMonth) return true;
  if (curMonth > expMonth) return false;
  return curDay <= expDay;
}

// ============================================================
void logTapEvent(String uid, bool isValid) {
  HTTPClient http;
  String url = "https://firestore.googleapis.com/v1/projects/";
  url += FIREBASE_PROJECT_ID;
  url += "/databases/(default)/documents/passengers/";
  url += uid + "/tap_history";

  http.begin(url);
  http.addHeader("Authorization", "Bearer " + idToken);
  http.addHeader("Content-Type", "application/json");

  time_t now; time(&now);
  char timeStr[32];
  strftime(timeStr, sizeof(timeStr), "%Y-%m-%dT%H:%M:%SZ", gmtime(&now));

  String body = "{\"fields\":{"
    "\"tappedAt\":{\"timestampValue\":\"" + String(timeStr) + "\"},"
    "\"isValid\":{\"booleanValue\":" + (isValid ? "true" : "false") + "},"
    "\"busId\":{\"stringValue\":\"BUS-001\"}"
    "}}";

  int code = http.POST(body);
  Serial.println("📝 Tap logged to Firestore — HTTP " + String(code));
  http.end();
}

// ============================================================
// ── Helpers ──────────────────────────────────────────────────
void lcdPrint(String line1, String line2) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(line1.substring(0, min((int)line1.length(), 16)));
  lcd.setCursor(0, 1);
  lcd.print(line2.substring(0, min((int)line2.length(), 16)));
}

void printBanner() {
  Serial.println();
  Serial.println("╔═══════════════════════════════════╗");
  Serial.println("║    RTC BUS PASS VALIDATOR v1.0    ║");
  Serial.println("║   ESP32 + RC522 + Firebase        ║");
  Serial.println("╚═══════════════════════════════════╝");
  Serial.println();
}

void printDivider() {
  Serial.println("─────────────────────────────────────");
}

// Pad a string to fixed width for table alignment
String padRight(String s, int width) {
  while ((int)s.length() < width) s += " ";
  if ((int)s.length() > width) s = s.substring(0, width);
  return s;
}
