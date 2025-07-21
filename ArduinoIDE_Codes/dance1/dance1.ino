#include <Servo.h>

// Create servo objects
Servo head;       // Servo 1
Servo leftHand;   // Servo 2
Servo rightHand;  // Servo 3

void setup() {
  Serial.begin(9600);

  head.attach(4);
  leftHand.attach(5);
  rightHand.attach(6);

  head.write(0);
  leftHand.write(0);
  rightHand.write(0);

  Serial.println("Setup complete. Starting advanced dance routine...");
}

void smoothMove(Servo &servo, int fromAngle, int toAngle, int stepDelay = 10) {
  if (fromAngle < toAngle) {
    for (int pos = fromAngle; pos <= toAngle; pos++) {
      servo.write(pos);
      delay(stepDelay);
    }
  } else {
    for (int pos = fromAngle; pos >= toAngle; pos--) {
      servo.write(pos);
      delay(stepDelay);
    }
  }
}

// Advanced head shake
void headShake() {
  Serial.println("Head shake");
  for (int i = 0; i < 2; i++) {
    smoothMove(head, 0, 30, 5);
    smoothMove(head, 30, -30, 5);
    smoothMove(head, -30, 0, 5);
  }
  head.write(0);
}

// Arm wave (smoother)
void waveArm(Servo &arm, const String &name) {
  Serial.println("Waving " + name);
  for (int i = 0; i < 3; i++) {
    smoothMove(arm, 0, 90, 5);
    smoothMove(arm, 90, 0, 5);
  }
}

// Dance sequence
void danceSequence() {
  // Head nod
  Serial.println("Head nod x2");
  for (int i = 0; i < 2; i++) {
    smoothMove(head, 0, 40, 5);
    smoothMove(head, 40, 0, 5);
  }

  // Alternate arms
  Serial.println("Alternating arm waves");
  waveArm(leftHand, "Left Hand");
  delay(200);
  waveArm(rightHand, "Right Hand");

  // Both arms together
  Serial.println("Both arms up");
  smoothMove(leftHand, 0, 90, 5);
  smoothMove(rightHand, 0, 90, 5);
  delay(400);

  // Head shake
  headShake();

  // Both arms down
  Serial.println("Arms down");
  smoothMove(leftHand, 90, 0, 5);
  smoothMove(rightHand, 90, 0, 5);
  delay(500);

  // Final pose
  Serial.println("Final Pose");
  head.write(20);
  leftHand.write(90);
  rightHand.write(90);
  delay(1000);

  // Reset
  Serial.println("Reset to Neutral");
  head.write(0);
  leftHand.write(0);
  rightHand.write(0);
  delay(1500);
}

void loop() {
  danceSequence();
}
