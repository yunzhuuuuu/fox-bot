#include <Adafruit_MotorShield.h>
#include <WiFiS3.h>
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

// Initialize Motor Shields
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
  Serial.begin(9600); // Start Serial first for debugging

  if (!ms1.begin()) { // Check if MS1 is found
    Serial.println("Failed to find MS1");
    while (1);
  }
  if (!ms2.begin()) { // Check if MS2 is found
    Serial.println("Failed to find MS2");
    while (1);
  }

  // --- All motor run() and setSpeed() commands are REMOVED from setup() ---
  Serial.println("Motor Shields OK");

  // Connect to WiFi
  while (status != WL_CONNECTED) {
    Serial.print("Attempting to connect to ");
    Serial.println(ssid);
    status = WiFi.begin(ssid, pass);
    delay(1000);
  }
  Serial.println("Connected to WiFi");
  
  Udp.begin(8081); // Start UDP listener
}

void loop() {
  // If there's a packet available read it
  int packetSize = Udp.parsePacket();
  if (packetSize) {
    // --- Motors only run WHEN a packet is received ---
    
    // Read the packet (though we aren't using the data yet)
    IPAddress remoteIp = Udp.remoteIP();
    int len = Udp.read(packetBuffer, 255);
    if (len > 0) {
      packetBuffer[len] = 0; // Make sure it's a null-terminated string
    }
    Serial.print("Received packet: ");
    Serial.println(packetBuffer);

    // Run motors as a test
    m11->run(BACKWARD);
    m11->setSpeed(150);
    m12->run(FORWARD);
    m12->setSpeed(150);
    
    delay(1000); // Run them for 1 second

    // STOP the motors
    m11->run(RELEASE);
    m12->run(RELEASE);
  }
  // If no packet is received, the loop repeats and motors remain off.
}