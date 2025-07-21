#include <Servo.h>

// Create Servo objects
Servo head;      // Pin 7
Servo leftArm;   // Pin 6
Servo rightArm;  // Pin 5

void setup() {
  head.attach(7);
  leftArm.attach(6);
  rightArm.attach(5);

  head.write(90);
  leftArm.write(90);
  rightArm.write(90);

}

void loop() {
  for (int i = 0; i < 3; i++) { // Dance loop 3 times
    // Head nod left to right
    head.write(60);
    delay(300);
    head.write(120);
    delay(300);
    head.write(90); // back to center
    delay(300);

    // Left arm up, right arm down
    leftArm.write(0);
    rightArm.write(180);
    delay(400);

    // Left arm down, right arm up
    leftArm.write(180);
    rightArm.write(0);
    delay(400);

    // Both arms to middle
    leftArm.write(90);
    rightArm.write(90);
    delay(400);

    // Quick wave
    for (int j = 0; j < 2; j++) {
      leftArm.write(60);
      rightArm.write(120);
      delay(200);
      leftArm.write(120);
      rightArm.write(60);
      delay(200);
    }
  }

  // End pose
  head.write(90);       // head center
  leftArm.write(90);    // arms relaxed
  rightArm.write(90);
  delay(2000);          // Pause before repeating the dance
}
