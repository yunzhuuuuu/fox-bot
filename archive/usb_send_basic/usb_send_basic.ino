const long SERIAL_BAUD_RATE = 1000000; // Fastest possible for heavy data loads

// Header markers for the start of data packets (used for synching audio)
// Need two headers to avoid a false positive
const uint8_t HEADER_BYTE_1 = 0xFF;
const uint8_t HEADER_BYTE_2 = 0xFE;

// Audio setup
const int MIC_PIN_1 = A0;
const int MIC_PIN_2 = A1;
const int MIC_PIN_3 = A2;
const int SAMPLE_RATE = 8000; // 8khz audio sampling
const int MIC_INTERVAL = 1000000 / SAMPLE_RATE; // Working in microseconds

// 243 * 3 channels = 729 total samples.
const int NUM_SAMPLE_INTERVALS = 243;
const int NUM_CHANNELS = 3;
const int TOTAL_BUFFER_SAMPLES = NUM_SAMPLE_INTERVALS * NUM_CHANNELS; // 729
const int BUFFER_SIZE_BYTES = TOTAL_BUFFER_SAMPLES * 2; // 1458 bytes (max is 1500 but save room for headers)

// Double audio buffer to reduce lag and blocking
int16_t audioBufferA[TOTAL_BUFFER_SAMPLES];
int16_t audioBufferB[TOTAL_BUFFER_SAMPLES];
int16_t* activeBuffer = audioBufferA;
int16_t* pendingBuffer = audioBufferB;

int bufferIndex = 0; // Used to track buffer pos

unsigned long lastSampleTime = 0; // Last time an audio sample was taken, important for maintaining 8khz


void setup() {
  // 10-bit ADC for audio quality
  analogReadResolution(10);

  Serial.begin(SERIAL_BAUD_RATE);

  while (!Serial) { // Wait for computer to connect
    delay(10); // Small delay to give the computer time
  }
}

void loop() {
  if (micros() - lastSampleTime >= MIC_INTERVAL) { // Check to see if 1/8000 of a second has passed
    lastSampleTime = micros(); // Record time sample is taken

    // Read mic inputs
    uint16_t sample_10bit_1 = analogRead(MIC_PIN_1); //A0
    uint16_t sample_10bit_2 = analogRead(MIC_PIN_2); //A1
    uint16_t sample_10bit_3 = analogRead(MIC_PIN_3); //A2

    // Center 10-bit sample (0-1023 -> -512 to 511) and scale to 16-bit for data transmisiion
    activeBuffer[bufferIndex + 0] = (int16_t)(sample_10bit_1 - 512) << 6; // Mic 1
    activeBuffer[bufferIndex + 1] = (int16_t)(sample_10bit_2 - 512) << 6; // Mic 2
    activeBuffer[bufferIndex + 2] = (int16_t)(sample_10bit_3 - 512) << 6; // Mic 3

    bufferIndex += 3; // Go up 3 since we have 3 channels

    // Check if the buffer is full (inded = 729 samples)
    if (bufferIndex >= TOTAL_BUFFER_SAMPLES) {
      // Exchange active/pending buffers
      int16_t* temp = activeBuffer;
      activeBuffer = pendingBuffer;
      pendingBuffer = temp;

      bufferIndex = 0;

      // Send header first
      Serial.write(HEADER_BYTE_1);
      Serial.write(HEADER_BYTE_2);
      
      // Send the raw byte data from the buffer
      Serial.write((uint8_t*)pendingBuffer, BUFFER_SIZE_BYTES); // Sends 1458 bytes
      
    }
  }
}