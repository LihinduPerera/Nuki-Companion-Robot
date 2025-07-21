#include <Servo.h>
#include <SoftwareSerial.h>

// Servo mapping: head : s1 , rightHand : s2, leftHand : s3
#define RX_PIN 8
#define TX_PIN 9

#define SERVO1_PIN 6
#define SERVO2_PIN 5
#define SERVO3_PIN 4

SoftwareSerial espSerial(RX_PIN, TX_PIN); // RX from ESP32, TX to ESP32

Servo servo1, servo2, servo3;

String inputString = "";
bool stringComplete = false;

void setup() {
  Serial.begin(9600);
  espSerial.begin(9600);

  servo1.attach(SERVO1_PIN);
  servo2.attach(SERVO2_PIN);
  servo3.attach(SERVO3_PIN);

  // Initialize to neutral position
  servo1.write(90);
  servo2.write(180);
  servo3.write(0);

  inputString.reserve(50);
  Serial.println("Servo Controller Ready.");
}

void loop() {
  while (espSerial.available()) {
    char inChar = (char)espSerial.read();
    if (inChar == '\n') {
      stringComplete = true;
      break;
    } else {
      inputString += inChar;
    }
  }

  if (stringComplete) {
    processCommand(inputString);
    inputString = "";
    stringComplete = false;
  }
}

void processCommand(String cmd) {
  cmd.trim();
  Serial.print("Received: ");
  Serial.println(cmd);

  if (cmd.startsWith("M")) {
    int servoNum = cmd.substring(1, 2).toInt();
    int colonIndex = cmd.indexOf(':');
    if (colonIndex > 1 && colonIndex < cmd.length() - 1) {
      int angle = cmd.substring(colonIndex + 1).toInt();
      angle = constrain(angle, 0, 180);

      switch (servoNum) {
        case 1: moveServoSmooth(servo1, angle); break;
        case 2: moveServoSmooth(servo2, angle); break;
        case 3: moveServoSmooth(servo3, angle); break;
        default: Serial.println("Invalid servo number."); break;
      }
    } else {
      Serial.println("Invalid format. Use M1:90");
    }
  } else if (cmd.startsWith("ACT")) {
    executeAction(cmd);
  } else {
    Serial.println("Unknown command.");
  }
}

void moveServoSmooth(Servo &servo, int target) {
  int current = servo.read();
  int step = (target > current) ? 1 : -1;

  for (int pos = current; pos != target; pos += step) {
    servo.write(pos);
    delay(5);
  }
  servo.write(target);
  delay(10);
}

void executeAction(String act) {
  if (act == "ACT1") {
    // Wave Right Hand
    for (int i = 0; i < 3; i++) {
      moveServoSmooth(servo2, 60);
      delay(200);
      moveServoSmooth(servo2, 120);
      delay(200);
    }
    moveServoSmooth(servo2, 180); // return to neutral
  }

  else if (act == "ACT2") {
    // Nod Head Yes
    for (int i = 0; i < 2; i++) {
      moveServoSmooth(servo1, 110);
      delay(200);
      moveServoSmooth(servo1, 70);
      delay(200);
    }
    moveServoSmooth(servo1, 90); // reset
  }

  else if (act == "ACT3") {
    // Shake Head No
    for (int i = 0; i < 2; i++) {
      moveServoSmooth(servo1, 80);
      delay(200);
      moveServoSmooth(servo1, 100);
      delay(200);
    }
    moveServoSmooth(servo1, 90);
  }

  else if (act == "ACT4") {
    // Raise both hands
    moveServoSmooth(servo2, 45); // Right hand up
    moveServoSmooth(servo3, 135); // Left hand up
    delay(500);
    moveServoSmooth(servo2, 180);
    moveServoSmooth(servo3, 0);
  }

  else if (act == "ACT5") {
    // Reset to neutral
    moveServoSmooth(servo1, 90);
    moveServoSmooth(servo2, 180);
    moveServoSmooth(servo3, 0);
  }

  else {
    Serial.println("Unknown action.");
  }
}
