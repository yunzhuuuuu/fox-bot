#include <WiFiS3.h>
#include <WiFiUdp.h> 

// User settings
char ssid[] = "jakewifi"; // WiFi name 
char pass[] = "12345678"; // WiFi password
IPAddress serverAddress(192, 168, 137, 1); // IP of the Python server
int serverPort = 8080; // Port of Python server

// Audio setup
const int MIC_PIN_1 = A1;
const int MIC_PIN_2 = A2;
const int MIC_PIN_3 = A3;
const int SAMPLE_RATE = 8000; 
const int MIC_INTERVAL = 1000000 / SAMPLE_RATE; 

// 243 * 3 channels = 729 total samples.
const int NUM_SAMPLE_INTERVALS = 243;
const int NUM_CHANNELS = 3;
const int TOTAL_BUFFER_SAMPLES = NUM_SAMPLE_INTERVALS * NUM_CHANNELS; // 729
const int BUFFER_SIZE_BYTES = TOTAL_BUFFER_SAMPLES * 2; // 1458 bytes (1500 is max)

// Create audio double buffer 
int16_t audioBufferA[TOTAL_BUFFER_SAMPLES];
int16_t audioBufferB[TOTAL_BUFFER_SAMPLES];
int16_t* activeBuffer = audioBufferA;
int16_t* pendingBuffer = audioBufferB;

int bufferIndex = 0; 

// WiFi setup
int status = WL_IDLE_STATUS;

WiFiUDP Udp; // Use UDP for speed, may lose data

unsigned long lastSampleTime = 0; 


void setup() {
  // Read 10-bit audio 
  analogReadResolution(10);
  while (status != WL_CONNECTED) {
    status = WiFi.begin(ssid, pass);
    delay(1000);
  }
  Udp.begin(8080); // Same as python
  }

void loop() {
  if (micros() - lastSampleTime >= MIC_INTERVAL) {
    lastSampleTime = micros(); 

    // Read mic inputs
    uint16_t sample_10bit_1 = analogRead(MIC_PIN_1);
    uint16_t sample_10bit_2 = analogRead(MIC_PIN_2);
    uint16_t sample_10bit_3 = analogRead(MIC_PIN_3);
    
    // Place each sample in the buffer in order
    activeBuffer[bufferIndex + 0] = (int16_t)(sample_10bit_1 - 512) << 6; // Channel 1
    activeBuffer[bufferIndex + 1] = (int16_t)(sample_10bit_2 - 512) << 6; // Channel 2
    activeBuffer[bufferIndex + 2] = (int16_t)(sample_10bit_3 - 512) << 6; // Channel 3
    
    bufferIndex += 3;

    // Check if the buffer is full (729 samples)
    if (bufferIndex >= TOTAL_BUFFER_SAMPLES) { 
        // Exchange active/pending buffers 
        int16_t* temp = activeBuffer;
        activeBuffer = pendingBuffer;
        pendingBuffer = temp;

        bufferIndex = 0; 

        // Send the pending buffer (already filled)
        Udp.beginPacket(serverAddress, serverPort);
        Udp.write((uint8_t*)pendingBuffer, BUFFER_SIZE_BYTES); // Sends 1458 bytes
        Udp.endPacket();
    }
  }
}

