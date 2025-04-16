#include <WiFi.h>
#include <WebServer.h>

// WiFi credentials
const char* ssid = "Gutlu";  // Replace with your WiFi name
const char* password = "dhanbad01";  // Replace with your WiFi password

// Global variable to track whistle status
bool whistleDetected = false;
unsigned long lastStatusUpdate = 0;

// Create web server on port 80
WebServer server(80);

// Simple HTML for the web page
String getHtmlPage() {
  String html = "<!DOCTYPE html><html>";
  html += "<head><meta charset='UTF-8'>";
  html += "<title>Whistle Detection</title>";
  html += "<meta name='viewport' content='width=device-width, initial-scale=1.0'>";
  html += "<meta http-equiv='refresh' content='5'>"; // Refresh every 5 seconds
  html += "<style>";
  html += "body{font-family:Arial,sans-serif;text-align:center;margin-top:50px;background-color:#f0f0f0;}";
  html += ".status{padding:20px;border-radius:8px;margin:20px auto;max-width:300px;}";
  html += ".detected{background-color:#ffcc00;color:black;}";
  html += ".clear{background-color:#4CAF50;color:white;}";
  html += ".offline{background-color:#f44336;color:white;}";
  html += "</style></head>";
  html += "<body><h1>Whistle Detection Status</h1>";
  
  // Check if status is recent (less than 20 seconds old)
  bool isRecent = (millis() - lastStatusUpdate) < 20000;
  
  if (!isRecent) {
    html += "<div class='status offline'><h2>OFFLINE</h2><p>No updates received recently</p></div>";
  } else if (whistleDetected) {
    html += "<div class='status detected'><h2>WHISTLE DETECTED!</h2></div>";
  } else {
    html += "<div class='status clear'><h2>Listening...</h2><p>No whistle detected</p></div>";
  }
  
  html += "</body></html>";
  return html;
}

void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  
  // Set up the web server routes - simplify and minimize the routes
  server.on("/", HTTP_GET, []() {
    server.send(200, "text/html", getHtmlPage());
  });
  
  // Simple status endpoint
  server.on("/status", HTTP_GET, []() {
    whistleDetected ? server.send(200, "text/plain", "detected") : 
                     server.send(200, "text/plain", "clear");
  });
  
  // Keep these endpoints very simple
  server.on("/whistle/detected", HTTP_GET, []() {
    whistleDetected = true;
    lastStatusUpdate = millis();
    server.send(200, "text/plain", "OK");
    Serial.println("Whistle detected!");
  });
  
  server.on("/whistle/clear", HTTP_GET, []() {
    whistleDetected = false;
    lastStatusUpdate = millis();
    server.send(200, "text/plain", "OK");
    Serial.println("Whistle cleared");
  });
  
  // Start the server
  server.begin();
  Serial.println("HTTP server started");
}

void loop() {
  // Just handle client requests - keep the loop as simple as possible
  server.handleClient();
  yield(); // Give the CPU some breathing room
}