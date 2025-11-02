#include <Adafruit_MotorShield.h>
#include <WiFiUdp.h>

// WiFi settings
char ssid[] = "jakewifi"; // WiFi name 
char pass[] = "12345678"; // WiFi password
IPAddress serverAddress(192, 168, 137, 1); // IP of the Python server
int serverPort = 8081; // Port of Python server
char packetBuffer[255]; //buffer to hold incoming packet

// WiFi Setup
int status = WL_IDLE_STATUS;
WiFiUDP Udp; // Use UDP for speed, may lose data

Adafruit_MotorShield ms1 = Adafruit_MotorShield(0x60);
Adafruit_MotorShield ms2 = Adafruit_MotorShield(0x61);

// Connect DC Motors
// MS1
Adafruit_DCMotor *m11 = ms1.getMotor(1); // Drive motor 1
Adafruit_DCMotor *m12 = ms1.getMotor(2); // Drive motor 2
// MS2
Adafruit_DCMotor *m21 = ms2.getMotor(1); // Ear motor 1
Adafruit_DCMotor *m22 = ms2.getMotor(2); // Rear motor 2 
Adafruit_DCMotor *m23 = ms2.getMotor(3); // Ear motor 1

void setup() {
  if (ms1.begin()) {
    Serial.begin(9600);
    m11->run(BACKWARD);
    m11->setSpeed(30);
    delay(200);
  }
  if (ms2.begin()) {
    m21->run(BACKWARD);
    m21->setSpeed(30);
    delay(200);
  }

  while (status != WL_CONNECTED) {
    status = WiFi.begin(ssid, pass);
    delay(1000);
  }
  Udp.begin(8081); // Same as python
}

void loop() {
  // If there's a packet available read it
  int packetSize = Udp.parsePacket();
  if (packetSize) {
    IPAddress remoteIp = Udp.remoteIP();
    int len = Udp.read(packetBuffer, 255);
    if (len > 0) {
      packetBuffer[len] = 0; // Make sure it doesn't double read
    }
    m11->run(BACKWARD);
    m12->run(FORWARD);
    delay(1000);
  }
}















