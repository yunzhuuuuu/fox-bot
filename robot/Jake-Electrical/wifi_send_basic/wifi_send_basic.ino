#include <WiFiS3.h>
#include <WiFiUdp.h> 

// User settings
char ssid[] = "jakewifi"; // WiFi name (SSID)
char pass[] = "12345678"; // WiFi password
IPAddress serverAddress(192, 168, 137, 1); // IP of the Python server
int serverPort = 8080; // Port for Python server

// Audio setup
int MIC_PIN = A0;
const int SAMPLE_RATE = 8000; 
const int MIC_INTERVAL = 1000000 / SAMPLE_RATE; 

// WiFi buffer configuration
const int BUFFER_SAMPLES = 730;
// Each sample is int16_t (2 bytes), so buffer is twice as large in bytes
const int BUFFER_SIZE_BYTES = BUFFER_SAMPLES * 2; 

// Create audio double buffer using 16-bit signed integers
int16_t audioBufferA[BUFFER_SAMPLES];
int16_t audioBufferB[BUFFER_SAMPLES];
int16_t* activeBuffer = audioBufferA;
int16_t* pendingBuffer = audioBufferB;
int bufferIndex = 0; 

// WiFi setup
int status = WL_IDLE_STATUS;
WiFiUDP Udp; 
unsigned long lastSampleTime = 0; 

void setup() {
  // Read at 10-bit resolution (0-1023)
  analogReadResolution(10);

  while (status != WL_CONNECTED) {
    status = WiFi.begin(ssid, pass);
    delay(1000);
  }
  Udp.begin(2390);
}

void loop() {
  if (micros() - lastSampleTime >= MIC_INTERVAL) {
    lastSampleTime = micros(); 

    // Read 10-bit sample (0-1023)
    uint16_t sample_10bit = analogRead(MIC_PIN);
    
    // Convert to 16-bit signed audio
    // 1. Subtract 512 to center the wave at 0 (range -512 to +511)
    // 2. Shift left by 6 to scale it to 16-bit range
    //    (Resulting range: -32768 to +32704)
    activeBuffer[bufferIndex] = (int16_t)(sample_10bit - 512) << 6;
    
    bufferIndex++;

    if (bufferIndex >= BUFFER_SAMPLES) { 
        // Swap active and pending buffers
        int16_t* temp = activeBuffer;
        activeBuffer = pendingBuffer;
        pendingBuffer = temp;

        // Reset index for the new active buffer
        bufferIndex = 0; 

        // Send the (now) pending buffer
        Udp.beginPacket(serverAddress, serverPort);
        // Cast our int16_t buffer to a raw byte pointer (uint8_t*)
        // and send the total number of *bytes*.
        Udp.write((uint8_t*)pendingBuffer, BUFFER_SIZE_BYTES);
        Udp.endPacket();
    }
  }
}
