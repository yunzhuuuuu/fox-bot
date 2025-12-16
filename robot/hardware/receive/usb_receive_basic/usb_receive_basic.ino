#include <Adafruit_MotorShield.h>
#include <Servo.h>
#include <LedControl.h>

// All pin defs
const int DIN_PIN = 12; // Data In (MOSI) -> Connect to DIN on the first display (orange wire)
const int CLK_PIN = 7; // Clock -> Connect to CLK on the first display (green wire)
const int CS_PIN = 8; // Load/Chip Select (CS) -> Connect to CS on the first display (yellow wire)
const int ENCODER_PIN_R = 2; // Encoder for right motor (must be 2 or 3 for ISR)
const int ENCODER_PIN_L = 3; // Encoder for left motor (must be 2 or 3 for ISR)
const int SERVO_EAR_R = 10; // Right ear servo
const int SERVO_EAR_L = 11; // Left ear servo
const int SERVO_TAIL = 6; // Tail servo

const int NUM_DEVICES = 2; // Number of displays daisy-chained together

byte SERIAL_PACKET_SIZE = 21; // Serial Comm Constants

// Motor shield setup
Adafruit_MotorShield MS1 = Adafruit_MotorShield(); // Motor shield (0x60 address)

// Attach motors
Adafruit_DCMotor *m1 = MS1.getMotor(4); // Left Drive Motor
Adafruit_DCMotor *m2 = MS1.getMotor(3); // Right Drive Motor

// Servo objects
Servo earR_servo;
Servo earL_servo;
Servo tail_servo;


// Set up LED controller
LedControl lc = LedControl(DIN_PIN, CLK_PIN, CS_PIN, NUM_DEVICES);

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
  for (int row = 0; row < PATTERN_ROWS; row++) { // Set patterns
    lc.setRow(0, row, leftArray[row]);
    lc.setRow(1, row, rightArray[row]);
  }
}

void setMotors(int speedL, int speedR) {
  // Clamps all speeds to 255
  if (speedL > 255){
    speedL = 255;
  }
  if (speedR < -255) {
    speedL = -255;
  }
    if (speedR > 255){
    speedL = 255;
  }
  if (speedR < -255) {
    speedR = -255;
  }
  
  // Set speed and direction of left motor
  if (speedL==0){
    m1 -> run(RELEASE);
  } else if(speedL<0){
    m1 -> run(BACKWARD);
    m1->setSpeed(-speedL);
  } else{
    m1 -> run(FORWARD);
    m1->setSpeed(speedL);
  }
  // Set speed and direction of right motor
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

void setEars(byte ear_angle) { // Set ears angle
  int ear_delta = ear_angle - 90;
  earR_servo.write(90 + ear_delta);
  earL_servo.write(90 - ear_delta);
}

void setTail(byte tail_angle) { // Set tail angle
  tail_servo.write(tail_angle);
}


void setup() {
  MS1.begin();
  //------------------------------------------------------------------------------------------------
  // The arduino code needs to receive a 21 byte array message to run 
  // 21 bytes = 168 bits
  // The robot should have a refresh rate of around 200-500 times a second for seameless operation 
  // Realistically 60hz or so would probably be fine but where is the fun in that
  // 168*500 = 84,000 which means 9600 is too slow so we need 115200 bps or faster
  //------------------------------------------------------------------------------------------------
  Serial.begin(115200); // Bitrate justified above
  delay(100); // Give time for Raspi to connect

  // Attach all necessary servos
  earR_servo.attach(SERVO_EAR_R);
  earL_servo.attach(SERVO_EAR_L);
  tail_servo.attach(SERVO_TAIL);


  lc.shutdown(0, false); // Wake up display 1
  lc.setIntensity(0, 1); // Set the brightness from 0-15 
  lc.clearDisplay(0); // Clear display 1
  lc.shutdown(1, false); // Wake up the display 2
  lc.setIntensity(1, 1); // Set the brightness from 0-15 
  lc.clearDisplay(1); // Clear display 2
  pinMode(9, INPUT_PULLUP); 
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
    
    if (Serial.readBytes(buffer, SERIAL_PACKET_SIZE) == SERIAL_PACKET_SIZE) { // Unpack message data
      int receivedLeftSpeed = (int)buffer[0];
      int receivedRightSpeed = (int)buffer[1];
      int leftSpeed = (receivedLeftSpeed - 128)*2; // Convert unsigned 0-255 to signed -255-255
      int rightSpeed = (receivedRightSpeed - 128)*2; // Convert unsigned 0-255 to signed -255-255
      int receivedEar = (int)buffer[2];
      int receivedTail = (int)buffer[3];
      int receivedBrightness = (int)buffer[4];

      for (int i = 0; i < 8; i++) { // Unpack array for left eye
        leftArray[i] = buffer[5 + i];
      }

      for (int i = 0; i < 8; i++) { // Unpack array for right eye
        rightArray[i] = buffer[13 + i];
      }

      setDisplays(receivedBrightness, leftArray, rightArray); // Set displays based on arrays unpacked above

      setMotors(leftSpeed, rightSpeed); // Set motors to speeds unpacked above

      if (l_receivedEar != receivedEar) { // Set ear angles
        setEars(receivedEar);
      }
      
      if (l_receivedTail != receivedTail) { // Set tail angle
        setTail(receivedTail);
      }

    }

    int buttonState = digitalRead(9);
    // Check if the button is pressed (LOW because of the pull-up resistor on the pin)
    if (buttonState == LOW) {
      Serial.print(1);
    } else {
      Serial.print(0);
    }s
  }
}