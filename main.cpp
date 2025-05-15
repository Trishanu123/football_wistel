#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "Gutlu";
const char* password = "dhanbad01";

WebServer server(80);

String statusMessage = "Listening...";
const int motorPin = 21; // GPIO 21 for motor

void handleRoot() {
  String html = "<html><head><meta http-equiv='refresh' content='1'></head><body><h1>Status: " + statusMessage + "</h1></body></html>";
  server.send(200, "text/html", html);
}

void handleWhistle() {
  statusMessage = "🎯 Whistle Detected!";
  Serial.println("Whistle Detected!");
  digitalWrite(motorPin, HIGH); // Turn ON motor
  delay(3000);                  // Run motor for 3 seconds
  digitalWrite(motorPin, LOW);  // Turn OFF motor
  Serial.println("Motor turned OFF");
  server.send(200, "text/plain", "Whistle detected, motor activated.");
}

void handleClear() {
  statusMessage = "Listening...";
  digitalWrite(motorPin, LOW); // Ensure motor is OFF
  Serial.println("Status cleared. Motor OFF.");
  server.send(200, "text/plain", "Status cleared.");
}

void setup() {
  Serial.begin(115200);

  pinMode(motorPin, OUTPUT);
  digitalWrite(motorPin, LOW); // Motor OFF initially

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Connecting...");
  }

  Serial.print("Connected! IP: ");
  Serial.println(WiFi.localIP());

  server.on("/", handleRoot);
  server.on("/whistle", handleWhistle);
  server.on("/clear", handleClear);

  server.begin();
}

void loop() {
  server.handleClient();
}

