#include <WiFiS3.h>
#include <WiFiUdp.h> 

// User settings
char ssid[] = "jakewifi"; // WiFi name (SSID)
char pass[] = "12345678"; // WiFi password
IPAddress serverAddress(192, 168, 137, 1); // IP of the Python server
int serverPort = 8081; // Port for Python server

// WiFi setup
int status = WL_IDLE_STATUS;
WiFiUDP Udp; 
char packetBuffer[255]; // Buffer to hold incoming packets

void setup() {
  Serial.begin(9600);
  delay(2000);
  Serial.println("Hi!");
  WiFi.begin(ssid, pass);
  while (status != WL_CONNECTED) {
    status = WiFi.begin(ssid, pass);
    delay(1000);
  Udp.begin(serverPort);
  }
}

void loop() {
  int packetSize = Udp.parsePacket();
  if (packetSize) {
    int len = Udp.read(packetBuffer, sizeof(packetBuffer));
    packetBuffer[len] = 0;
    Serial.println(packetBuffer);
  }
  memset(packetBuffer, 0, sizeof(packetBuffer));
}



