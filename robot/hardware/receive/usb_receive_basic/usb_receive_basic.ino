#include <Adafruit_MotorShield.h>
#include <Servo.h>
#include <LedControl.h>

// All pin defs
const int DIN_PIN = 12; // Data In (MOSI) -> Connect to DIN on the first display (orange wire)
const int CLK_PIN = 8; // Clock -> Connect to CLK on the first display (green wire)
const int CS_PIN = 7; // Load/Chip Select (CS) -> Connect to CS on the first display (yellow wire)
const int ENCODER_PIN_R = 2; // Encoder for right motor (must be 2 or 3 for ISR)
const int ENCODER_PIN_L = 3; // Encoder for left motor (must be 2 or 3 for ISR)
const int SERVO_EAR_R = 10; // Right ear servo
const int SERVO_EAR_L = 9; // Left ear servo
const int SERVO_TAIL = 6; // Tail servo

const int NUM_DEVICES = 2; // Number of displays daisy-chained together

// Motor shield setup
Adafruit_MotorShield MS1 = Adafruit_MotorShield(0x61); // Motor shield (0x61 address)

// Attach motors
Adafruit_DCMotor *m1 = MS1.getMotor(1); // Left Drive Motor
Adafruit_DCMotor *m2 = MS1.getMotor(2); // Right Drive Motor

// Servo objects
Servo earR_servo;
Servo earL_servo;
Servo tail_servo;


// Set up LED controller
LedControl lc = LedControl(DIN_PIN, CLK_PIN, CS_PIN, NUM_DEVICES);


const float WHEEL_DIAMETER_CM = 6.5; // Diameter of the drive wheels 
const float TRACK_WIDTH_CM = 15.0;   // Distance between the center of the wheels 
const int ENCODER_PPR = 11;          // Pulses per Revolution of the encoder
const float GEAR_REDUCTION = 34.0;  // Gearbox reduction ratio 
const float TOTAL_ENCODER_PPR = ENCODER_PPR * GEAR_REDUCTION; // Total pulses per wheel revolution

// Calculated constants
const float WHEEL_CIRCUMFERENCE_CM = PI * WHEEL_DIAMETER_CM;
// Pulses needed for 1 degree of robot turn 
const float PULSES_PER_DEGREE = (PI * TRACK_WIDTH_CM / 360.0) / WHEEL_CIRCUMFERENCE_CM * TOTAL_ENCODER_PPR;

// Encoder pulse counting 
volatile long rightEncoderCount = 0;
volatile long leftEncoderCount = 0;

int receivedLeftSpeed = 0;
int receivedRightSpeed = 0;
int receivedEar = 90;
int receivedTail = 90;
int receivedBrightness = 5;

int l_receivedLeftSpeed = 0;
int l_receivedRightSpeed = 0;
int l_receivedEar = 90;
int l_receivedTail = 90;
int l_receivedBrightness = 5;




// Serial Comm Constants
byte SERIAL_PACKET_SIZE = 14;

void ISR_Right() {
  rightEncoderCount++;
}

void ISR_Left() {
  leftEncoderCount++;
}

byte leftArray[] = {
  B00000000, // Row 0
  B00000000, // Row 1
  B00000000, // Row 2
  B00000000, // Row 3
  B00000000, // Row 4
  B00000000, // Row 5
  B00000000, // Row 6
  B00000000  // Row 7
};

byte rightArray[] = {
  B00000000, // Row 0
  B00000000, // Row 1
  B00000000, // Row 2
  B00000000, // Row 3
  B00000000, // Row 4
  B00000000, // Row 5
  B00000000, // Row 6
  B00000000  // Row 7
};

const int PATTERN_ROWS = 8; // Max number of rows in the pattern

void setDisplays(int brightness, byte leftArray[], byte rightArray[]) {
  lc.setIntensity(0, brightness); // Set the brightness from 0-15 
  lc.setIntensity(1, brightness); // Set the brightness from 0-15  
  for (int row = 0; row < PATTERN_ROWS; row++) { // Implement patterns
    lc.setRow(0, row, leftArray[row]);
    lc.setRow(1, row, rightArray[row]);
  }
}

void setMotorsForRotation(int speed, int delta) {
  long targetPulses = abs(delta) * PULSES_PER_DEGREE;
    uint8_t leftDirection, rightDirection;

  if (delta > 0) { // Positive delta = Turn Right 
    leftDirection = FORWARD;
    rightDirection = BACKWARD;
  } else if (delta < 0) { // Negative delta = Turn Left 
    leftDirection = BACKWARD;
    rightDirection = FORWARD;
  } else { // delta == 0
    m1->run(RELEASE);
    m2->run(RELEASE);
    return;
  }
  
  rightEncoderCount = 0;
  leftEncoderCount = 0;

  m1->run(leftDirection);
  m2->run(rightDirection);
  m1->setSpeed(speed);
  m2->setSpeed(speed);
  
  long maxPulses = 0;

  while (maxPulses < targetPulses) {
    long currentLeft = leftEncoderCount;
    long currentRight = rightEncoderCount;
    
    maxPulses = max(currentLeft, currentRight);
    
    m1->setSpeed(speed);
    m2->setSpeed(speed);

    m1->run(leftDirection);
    m2->run(rightDirection);
    
    delay(1); 
  }
  m1->run(RELEASE);
  m2->run(RELEASE);
  delay(50);
}

void setMotors(int speedL, int speedR) {

  if (speedL==0){
    m1 -> run(RELEASE);
  } else if(speedL<0){
    m1 -> run(BACKWARD);
    m1->setSpeed(-speedL);
  } else{
    m1 -> run(FORWARD);
    m1->setSpeed(speedL);
  }

  if (speedR==0){
    m2 -> run(RELEASE);
  } else if(speedR<0){
    m2 -> run(BACKWARD);
    m2->setSpeed(-speedR);
  } else{
    m2 -> run(FORWARD);
    m2->setSpeed(speedR);
  }
  
}

void setEars(byte ear_angle) {
  earR_servo.write(ear_angle);
  earL_servo.write(ear_angle);
}

void setTail(byte tail_angle) {
  tail_servo.write(tail_angle);
}


void setup() {
  MS1.begin();
  //------------------------------------------------------------------------------------------------
  // The arduino code needs to receive a 14 byte array message to run 
  // 14 bytes = 112 bits
  // The robot should have a refresh rate of around 200-500 times a second for seameless operation 
  // Realistically 60hz or so would probably be fine but where is the fun in that
  // 112*500 = 56,000 which means 9600 is too slow so we need 115200 bps or faster
  //------------------------------------------------------------------------------------------------
  Serial.begin(115200);
  delay(100); // Give time for computer to connect

  // These ISRs are for the encoders
  // Each encoder only needs to be measured on the rising side
  attachInterrupt(digitalPinToInterrupt(ENCODER_PIN_R), ISR_Right, RISING);
  attachInterrupt(digitalPinToInterrupt(ENCODER_PIN_L), ISR_Left, RISING);

  earR_servo.attach(SERVO_EAR_R);
  earL_servo.attach(SERVO_EAR_L);
  tail_servo.attach(SERVO_TAIL);


  lc.shutdown(0, false); // Wake up display 1
  lc.setIntensity(0, 1); // Set the brightness from 0-15 
  lc.clearDisplay(0); // Clear display 1
  lc.shutdown(1, false); // Wake up the display 2
  lc.setIntensity(1, 1); // Set the brightness from 0-15 
  lc.clearDisplay(1); // Clear display 2
}

void loop() {
  if (Serial.available() >= SERIAL_PACKET_SIZE) {
    byte buffer[SERIAL_PACKET_SIZE];

    // ----------------------------------------------------------
    // Serial Data format:
    // Byte 0 = Left motor speed -128-127(byte)
    // Byte 1 = Right motor speed -128-127(byte)
    // Byte 2 = Servo angle for ears 0-180(byte)
    // Byte 3 = Servo angle for the tail 0-180(byte)
    // Byte 4 = Eye brightness (0-1 -> scaled to 0-255)
    // Bytes 5-12 = Array for left eye (8 bytes)
    // Bytes 13-20 = Array for right eye (8 bytes)
    // ----------------------------------------------------------
    
    if (Serial.readBytes(buffer, SERIAL_PACKET_SIZE) == SERIAL_PACKET_SIZE) {
      int receivedLeftSpeed = (int)buffer[0];
      int receivedRightSpeed = (int)buffer[1];
      int receivedEar = (int)buffer[3];
      int receivedTail = (int)buffer[4];
      int receivedBrightness = (int)buffer[5];

      for (int i = 0; i < 8; i++) {
        leftArray[i] = buffer[5 + i];
      }

      for (int i = 0; i < 8; i++) {
        rightArray[i] = buffer[13 + i];
      }

      setDisplays(receivedBrightness, leftArray, rightArray);

      if ((l_receivedLeftSpeed != receivedLeftSpeed) || (l_receivedRightSpeed != receivedRightSpeed)) {
        setMotors(receivedLeftSpeed, receivedRightSpeed);
      }

      if (l_receivedEar != receivedEar) {
        setEars(receivedEar);
      }
      
      if (l_receivedTail != receivedTail) {
        setEars(receivedTail);
      }

    }
  }
}