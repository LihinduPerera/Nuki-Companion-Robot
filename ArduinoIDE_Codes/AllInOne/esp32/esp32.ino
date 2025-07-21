#include <WiFi.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET     -1
#define SCREEN_ADDRESS 0x3C

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Communication with Arduino
#define RXD2 16
#define TXD2 17

// Motor pins for L298N
#define IN1 25
#define IN2 26
#define IN3 27
#define IN4 14

const char* ssid = "MT20_MIFI_GEN-66";
const char* password = "9g8P604?";

IPAddress local_IP(192, 168, 8, 160);
IPAddress gateway(192, 168, 8, 1);    // Typically your router's IP
IPAddress subnet(255, 255, 255, 0);
IPAddress primaryDNS(8, 8, 8, 8);     // Optional
IPAddress secondaryDNS(8, 8, 4, 4);   // Optional

WiFiServer server(80);

// Eye animation variables
int demo_mode = 1;
static const int max_animation_index = 8;
int current_animation_index = 0;

// Reference state
int ref_eye_height = 40;
int ref_eye_width = 40;
int ref_space_between_eye = 10;
int ref_corner_radius = 10;

// Current state of the eyes
int left_eye_height = ref_eye_height;
int left_eye_width = ref_eye_width;
int left_eye_x = 32;
int left_eye_y = 32;
int right_eye_x = 32 + ref_eye_width + ref_space_between_eye;
int right_eye_y = 32;
int right_eye_height = ref_eye_height;
int right_eye_width = ref_eye_width;

// Movement timing
unsigned long moveStartTime = 0;
unsigned long moveDuration = 0;
bool moving = false;

enum MoveDirection {
  NONE,
  FORWARD,
  BACKWARD,
  LEFT,
  RIGHT
};

MoveDirection currentMove = NONE;

void draw_eyes(bool update=true) {
    display.clearDisplay();

    // Left eye
    int x = int(left_eye_x - left_eye_width / 2);
    int y = int(left_eye_y - left_eye_height / 2);
    display.fillRoundRect(x, y, left_eye_width, left_eye_height, ref_corner_radius, SSD1306_WHITE);

    // Right eye
    x = int(right_eye_x - right_eye_width / 2);
    y = int(right_eye_y - right_eye_height / 2);
    display.fillRoundRect(x, y, right_eye_width, right_eye_height, ref_corner_radius, SSD1306_WHITE);

    if (update) {
        display.display();
    }
}

void center_eyes(bool update=true) {
    left_eye_height = ref_eye_height;
    left_eye_width = ref_eye_width;
    right_eye_height = ref_eye_height;
    right_eye_width = ref_eye_width;

    left_eye_x = SCREEN_WIDTH / 2 - ref_eye_width / 2 - ref_space_between_eye / 2;
    left_eye_y = SCREEN_HEIGHT / 2;
    right_eye_x = SCREEN_WIDTH / 2 + ref_eye_width / 2 + ref_space_between_eye / 2;
    right_eye_y = SCREEN_HEIGHT / 2;

    draw_eyes(update);
}

void blink(int speed=12) {
    draw_eyes();
    for (int i = 0; i < 3; i++) {
        left_eye_height = left_eye_height - speed;
        right_eye_height = right_eye_height - speed;
        draw_eyes();
        delay(1);
    }
    for (int i = 0; i < 3; i++) {
        left_eye_height = left_eye_height + speed;
        right_eye_height = right_eye_height + speed;
        draw_eyes();
        delay(1);
    }
}

void sleep() {
    left_eye_height = 2;
    right_eye_height = 2;
    draw_eyes(true);
}

void wakeup() {
    sleep();
    for (int h = 0; h <= ref_eye_height; h += 2) {
        left_eye_height = h;
        right_eye_height = h;
        draw_eyes(true);
    }
}

void happy_eye() {
    center_eyes(false);
    int offset = ref_eye_height / 2;
    for (int i = 0; i < 10; i++) {
        display.fillTriangle(left_eye_x - left_eye_width / 2 - 1, left_eye_y + offset,
                             left_eye_x + left_eye_width / 2 + 1, left_eye_y + 5 + offset,
                             left_eye_x - left_eye_width / 2 - 1, left_eye_y + left_eye_height + offset, SSD1306_BLACK);

        display.fillTriangle(right_eye_x + right_eye_width / 2 + 1, right_eye_y + offset,
                             right_eye_x - left_eye_width / 2 - 1, right_eye_y + 5 + offset,
                             right_eye_x + right_eye_width / 2 + 1, right_eye_y + right_eye_height + offset, SSD1306_BLACK);

        offset -= 2;
        display.display();
        delay(1);
    }
    display.display();
    delay(1000);
}

void loveEyes() {
    demo_mode = 0;
    center_eyes(false); // Clear the display
    
    // Draw two hearts
    for (int size = 5; size <= 15; size += 2) {
        display.clearDisplay();
        
        // Left heart
        display.fillCircle(32 - size/2, 32 - size/4, size/2, SSD1306_WHITE);
        display.fillCircle(32 + size/2, 32 - size/4, size/2, SSD1306_WHITE);
        display.fillTriangle(32 - size, 32 - size/4, 
                            32 + size, 32 - size/4, 
                            32, 32 + size, SSD1306_WHITE);
        
        // Right heart
        display.fillCircle(96 - size/2, 32 - size/4, size/2, SSD1306_WHITE);
        display.fillCircle(96 + size/2, 32 - size/4, size/2, SSD1306_WHITE);
        display.fillTriangle(96 - size, 32 - size/4, 
                            96 + size, 32 - size/4, 
                            96, 32 + size, SSD1306_WHITE);
        
        display.display();
        delay(50);
    }
    
    // Make hearts pulse
    for (int i = 0; i < 3; i++) {
        // Grow
        for (int size = 15; size <= 20; size += 1) {
            display.clearDisplay();
            
            // Left heart
            display.fillCircle(32 - size/2, 32 - size/4, size/2, SSD1306_WHITE);
            display.fillCircle(32 + size/2, 32 - size/4, size/2, SSD1306_WHITE);
            display.fillTriangle(32 - size, 32 - size/4, 
                                32 + size, 32 - size/4, 
                                32, 32 + size, SSD1306_WHITE);
            
            // Right heart
            display.fillCircle(96 - size/2, 32 - size/4, size/2, SSD1306_WHITE);
            display.fillCircle(96 + size/2, 32 - size/4, size/2, SSD1306_WHITE);
            display.fillTriangle(96 - size, 32 - size/4, 
                                96 + size, 32 - size/4, 
                                96, 32 + size, SSD1306_WHITE);
            
            display.display();
            delay(20);
        }
        
        // Shrink
        for (int size = 20; size >= 15; size -= 1) {
            display.clearDisplay();
            
            // Left heart
            display.fillCircle(32 - size/2, 32 - size/4, size/2, SSD1306_WHITE);
            display.fillCircle(32 + size/2, 32 - size/4, size/2, SSD1306_WHITE);
            display.fillTriangle(32 - size, 32 - size/4, 
                                32 + size, 32 - size/4, 
                                32, 32 + size, SSD1306_WHITE);
            
            // Right heart
            display.fillCircle(96 - size/2, 32 - size/4, size/2, SSD1306_WHITE);
            display.fillCircle(96 + size/2, 32 - size/4, size/2, SSD1306_WHITE);
            display.fillTriangle(96 - size, 32 - size/4, 
                                96 + size, 32 - size/4, 
                                96, 32 + size, SSD1306_WHITE);
            
            display.display();
            delay(20);
        }
    }
    
    // Final small hearts
    display.clearDisplay();
    int final_size = 12;
    
    // Left heart
    display.fillCircle(32 - final_size/2, 32 - final_size/4, final_size/2, SSD1306_WHITE);
    display.fillCircle(32 + final_size/2, 32 - final_size/4, final_size/2, SSD1306_WHITE);
    display.fillTriangle(32 - final_size, 32 - final_size/4, 
                        32 + final_size, 32 - final_size/4, 
                        32, 32 + final_size, SSD1306_WHITE);
    
    // Right heart
    display.fillCircle(96 - final_size/2, 32 - final_size/4, final_size/2, SSD1306_WHITE);
    display.fillCircle(96 + final_size/2, 32 - final_size/4, final_size/2, SSD1306_WHITE);
    display.fillTriangle(96 - final_size, 32 - final_size/4, 
                        96 + final_size, 32 - final_size/4, 
                        96, 32 + final_size, SSD1306_WHITE);
    
    display.display();
    delay(1000);
    center_eyes();
}

void saccade(int direction_x, int direction_y) {
    int direction_x_movement_amplitude = 8;
    int direction_y_movement_amplitude = 6;
    int blink_amplitude = 8;

    left_eye_x += direction_x_movement_amplitude * direction_x;
    right_eye_x += direction_x_movement_amplitude * direction_x;
    left_eye_y += direction_y_movement_amplitude * direction_y;
    right_eye_y += direction_y_movement_amplitude * direction_y;

    right_eye_height -= blink_amplitude;
    left_eye_height -= blink_amplitude;
    draw_eyes();
    delay(1);

    left_eye_x += direction_x_movement_amplitude * direction_x;
    right_eye_x += direction_x_movement_amplitude * direction_x;
    left_eye_y += direction_y_movement_amplitude * direction_y;
    right_eye_y += direction_y_movement_amplitude * direction_y;

    right_eye_height += blink_amplitude;
    left_eye_height += blink_amplitude;

    draw_eyes();
    delay(1);
}

void move_big_eye(int direction) {
    int direction_oversize = 1;
    int direction_movement_amplitude = 2;
    int blink_amplitude = 5;

    for (int i = 0; i < 3; i++) {
        left_eye_x += direction_movement_amplitude * direction;
        right_eye_x += direction_movement_amplitude * direction;

        right_eye_height -= blink_amplitude;
        left_eye_height -= blink_amplitude;

        if (direction > 0) {
            right_eye_height += direction_oversize;
            right_eye_width += direction_oversize;
        }
        else {
            left_eye_height += direction_oversize;
            left_eye_width += direction_oversize;
        }

        draw_eyes();
        delay(1);
    }
    for (int i = 0; i < 3; i++) {
        left_eye_x += direction_movement_amplitude * direction;
        right_eye_x += direction_movement_amplitude * direction;
        right_eye_height += blink_amplitude;
        left_eye_height += blink_amplitude;

        if (direction > 0) {
            right_eye_height += direction_oversize;
            right_eye_width += direction_oversize;
        }
        else {
            left_eye_height += direction_oversize;
            left_eye_width += direction_oversize;
        }
        draw_eyes();
        delay(1);
    }

    delay(1000);

    for (int i = 0; i < 3; i++) {
        left_eye_x -= direction_movement_amplitude * direction;
        right_eye_x -= direction_movement_amplitude * direction;

        right_eye_height -= blink_amplitude;
        left_eye_height -= blink_amplitude;

        if (direction > 0) {
            right_eye_height -= direction_oversize;
            right_eye_width -= direction_oversize;
        }
        else {
            left_eye_height -= direction_oversize;
            left_eye_width -= direction_oversize;
        }

        draw_eyes();
        delay(1);
    }
    for (int i = 0; i < 3; i++) {
        left_eye_x -= direction_movement_amplitude * direction;
        right_eye_x -= direction_movement_amplitude * direction;

        right_eye_height += blink_amplitude;
        left_eye_height += blink_amplitude;

        if (direction > 0) {
            right_eye_height -= direction_oversize;
            right_eye_width -= direction_oversize;
        }
        else {
            left_eye_height -= direction_oversize;
            left_eye_width -= direction_oversize;
        }
        draw_eyes();
        delay(1);
    }
    center_eyes();
}

void move_right_big_eye() {
    move_big_eye(1);
}

void move_left_big_eye() {
    move_big_eye(-1);
}

void sad_eye() {
    center_eyes(false);

    // Draw eyelids slanting down on the outer edges
    int lid_thickness = 4;
    int lid_slant = 6;

    // Left eye upper lid (slant down to left)
    display.fillRect(left_eye_x - left_eye_width / 2, left_eye_y - left_eye_height / 2, left_eye_width, lid_thickness, SSD1306_BLACK);
    display.fillTriangle(left_eye_x - left_eye_width / 2, left_eye_y - left_eye_height / 2,
                         left_eye_x - left_eye_width / 2 + lid_slant, left_eye_y - left_eye_height / 2 + lid_thickness,
                         left_eye_x - left_eye_width / 2, left_eye_y - left_eye_height / 2 + lid_thickness, SSD1306_BLACK);

    // Right eye upper lid (slant down to right)
    display.fillRect(right_eye_x - right_eye_width / 2, right_eye_y - right_eye_height / 2, right_eye_width, lid_thickness, SSD1306_BLACK);
    display.fillTriangle(right_eye_x + right_eye_width / 2, right_eye_y - right_eye_height / 2,
                         right_eye_x + right_eye_width / 2 - lid_slant, right_eye_y - right_eye_height / 2 + lid_thickness,
                         right_eye_x + right_eye_width / 2, right_eye_y - right_eye_height / 2 + lid_thickness, SSD1306_BLACK);

    // Draw small teardrop under left eye
    display.fillCircle(left_eye_x - left_eye_width / 4, left_eye_y + left_eye_height / 2 + 4, 2, SSD1306_WHITE);
    display.fillTriangle(left_eye_x - left_eye_width / 4, left_eye_y + left_eye_height / 2 + 4,
                         left_eye_x - left_eye_width / 4 + 2, left_eye_y + left_eye_height / 2 + 6,
                         left_eye_x - left_eye_width / 4 - 2, left_eye_y + left_eye_height / 2 + 6, SSD1306_WHITE);

    display.display();
    delay(1000);
}

void surprised_eye() {
    for (int s = 0; s <= 20; s += 4) {
        left_eye_height = ref_eye_height + s;
        right_eye_height = ref_eye_height + s;
        left_eye_width = ref_eye_width + s;
        right_eye_width = ref_eye_width + s;
        center_eyes(false);

        // Draw pupils (black circle)
        int pupil_radius = (ref_eye_height + s) / 6;
        display.fillCircle(left_eye_x, left_eye_y, pupil_radius, SSD1306_BLACK);
        display.fillCircle(right_eye_x, right_eye_y, pupil_radius, SSD1306_BLACK);

        // Draw highlight dots (small white circle)
        display.fillCircle(left_eye_x - pupil_radius / 2, left_eye_y - pupil_radius / 2, 1, SSD1306_WHITE);
        display.fillCircle(right_eye_x - pupil_radius / 2, right_eye_y - pupil_radius / 2, 1, SSD1306_WHITE);

        display.display();
        delay(50);
    }
    delay(1000);
    center_eyes();
}

void angry_eye() {
    center_eyes(false);

    int brow_thickness = 3;
    int brow_height = 6;

    // Left brow - thick slant down towards center
    for (int i = 0; i < brow_thickness; i++) {
        display.drawLine(left_eye_x - left_eye_width / 2, left_eye_y - left_eye_height / 2 - brow_height + i,
                         left_eye_x + left_eye_width / 2, left_eye_y - left_eye_height / 2 + i, SSD1306_WHITE);
    }

    // Right brow - thick slant down towards center
    for (int i = 0; i < brow_thickness; i++) {
        display.drawLine(right_eye_x - right_eye_width / 2, right_eye_y - right_eye_height / 2 + i,
                         right_eye_x + right_eye_width / 2, right_eye_y - right_eye_height / 2 - brow_height + i, SSD1306_WHITE);
    }

    // Furrowed brow (vertical lines between eyes)
    int furrow_x = SCREEN_WIDTH / 2;
    int furrow_y_start = left_eye_y - left_eye_height / 2 - brow_height / 2;
    int furrow_y_end = left_eye_y - left_eye_height / 2 + brow_height / 2;
    for (int i = -1; i <= 1; i++) {
        display.drawLine(furrow_x + i, furrow_y_start, furrow_x + i, furrow_y_end, SSD1306_WHITE);
    }

    display.display();
    delay(1000);
}

void wink_left_eye() {
    center_eyes(false);

    int steps = 6;
    for (int i = 0; i <= steps; i++) {
        left_eye_height = ref_eye_height - (ref_eye_height * i / steps);
        draw_eyes(false);

        // Draw a horizontal eyelid line to simulate closing
        int x1 = left_eye_x - left_eye_width / 2;
        int x2 = left_eye_x + left_eye_width / 2;
        int y = left_eye_y + left_eye_height / 2;
        display.drawLine(x1, y, x2, y, SSD1306_BLACK);

        display.display();
        delay(50);
    }

    delay(500);

    for (int i = steps; i >= 0; i--) {
        left_eye_height = ref_eye_height - (ref_eye_height * i / steps);
        draw_eyes(false);

        int x1 = left_eye_x - left_eye_width / 2;
        int x2 = left_eye_x + left_eye_width / 2;
        int y = left_eye_y + left_eye_height / 2;
        display.drawLine(x1, y, x2, y, SSD1306_BLACK);

        display.display();
        delay(50);
    }
    center_eyes();
}

void launch_animation_with_index(int animation_index) {
    if (animation_index > max_animation_index) {
        animation_index = 8;
    }

    switch (animation_index) {
        case 0:
            wakeup();
            break;
        case 1:
            center_eyes(true);
            break;
        case 2:
            move_right_big_eye();
            break;
        case 3:
            move_left_big_eye();
            break;
        case 4:
            blink(10);
            break;
        case 5:
            blink(20);
            break;
        case 6:
            happy_eye();
            break;
        case 7:
            sleep();
            break;
        case 8:
            center_eyes(true);
            for (int i = 0; i < 20; i++) {
                int dir_x = random(-1, 2);
                int dir_y = random(-1, 2);
                saccade(dir_x, dir_y);
                delay(1);
                saccade(-dir_x, -dir_y);
                delay(1);
            }
            break;
    }
}

void animateEyesForMovement(MoveDirection dir) {
    switch(dir) {
        case FORWARD:
            // Eyes look forward with slight widening
            left_eye_width = ref_eye_width + 5;
            right_eye_width = ref_eye_width + 5;
            draw_eyes();
            break;
        case BACKWARD:
            // Eyes look concerned (smaller and higher)
            left_eye_height = ref_eye_height - 5;
            right_eye_height = ref_eye_height - 5;
            left_eye_y -= 2;
            right_eye_y -= 2;
            draw_eyes();
            break;
        case LEFT:
            // Eyes look to the left
            left_eye_x -= 5;
            right_eye_x -= 5;
            draw_eyes();
            break;
        case RIGHT:
            // Eyes look to the right
            left_eye_x += 5;
            right_eye_x += 5;
            draw_eyes();
            break;
        case NONE:
            // Return to center
            center_eyes();
            break;
    }
}

void moveAround() {
    Serial.println("Starting move around pattern");
    demo_mode = 0;
    
    // Initial animation
    surprised_eye();
    delay(500);
    
    // Move forward
    animateEyesForMovement(FORWARD);
    moveForward(1500);
    delay(1500);
    
    // Turn right
    animateEyesForMovement(RIGHT);
    moveRight(800);
    delay(800);
    
    // Move forward
    animateEyesForMovement(FORWARD);
    moveForward(1500);
    delay(1500);
    
    // Turn left
    animateEyesForMovement(LEFT);
    moveLeft(800);
    delay(800);
    
    // Move backward
    animateEyesForMovement(BACKWARD);
    moveBackward(1500);
    delay(1500);
    
    // Turn right
    animateEyesForMovement(RIGHT);
    moveRight(800);
    delay(800);
    
    // Stop and happy animation
    stopMovement();
    animateEyesForMovement(NONE);
    happy_eye();
}

void figureEight() {
    Serial.println("Starting figure eight pattern");
    demo_mode = 0;
    
    // Initial animation
    for (int i = 0; i < 3; i++) {
        blink(15);
        delay(200);
    }
    
    // First loop of the 8
    animateEyesForMovement(FORWARD);
    moveForward(1000);
    delay(1000);
    
    animateEyesForMovement(RIGHT);
    moveRight(700);
    delay(700);
    
    animateEyesForMovement(FORWARD);
    moveForward(1000);
    delay(1000);
    
    animateEyesForMovement(RIGHT);
    moveRight(700);
    delay(700);
    
    // Second loop of the 8
    animateEyesForMovement(FORWARD);
    moveForward(1000);
    delay(1000);
    
    animateEyesForMovement(LEFT);
    moveLeft(700);
    delay(700);
    
    animateEyesForMovement(FORWARD);
    moveForward(1000);
    delay(1000);
    
    animateEyesForMovement(LEFT);
    moveLeft(700);
    delay(700);
    
    // Final animation
    stopMovement();
    animateEyesForMovement(NONE);
    for (int i = 0; i < 2; i++) {
        move_right_big_eye();
        move_left_big_eye();
    }
}

void cautiousExplore() {
    Serial.println("Starting cautious exploration");
    demo_mode = 0;
    
    // Initial animation - look around
    for (int i = 0; i < 5; i++) {
        animateEyesForMovement(LEFT);
        delay(200);
        animateEyesForMovement(RIGHT);
        delay(200);
    }
    animateEyesForMovement(NONE);
    
    for (int i = 0; i < 3; i++) {
        // Move forward with short steps
        animateEyesForMovement(FORWARD);
        moveForward(800);
        delay(800);
        stopMovement();
        
        // Look around animation
        animateEyesForMovement(LEFT);
        delay(300);
        animateEyesForMovement(RIGHT);
        delay(300);
        animateEyesForMovement(NONE);
        delay(300);
        
        // Turn slightly
        if (i % 2 == 0) {
            animateEyesForMovement(RIGHT);
            moveRight(400);
        } else {
            animateEyesForMovement(LEFT);
            moveLeft(400);
        }
        delay(400);
    }
    
    // Final animation
    stopMovement();
    animateEyesForMovement(NONE);
    blink(20);
}

void dance() {
    Serial.println("Starting dance routine");
    demo_mode = 0;
    
    // Initial animation
    surprised_eye();
    delay(300);
    happy_eye();
    delay(300);
    
    // Body movements with synchronized eye animations
    for (int i = 0; i < 2; i++) {
        animateEyesForMovement(LEFT);
        moveLeft(300);
        delay(300);
        
        animateEyesForMovement(RIGHT);
        moveRight(300);
        delay(300);
    }
    
    for (int i = 0; i < 3; i++) {
        animateEyesForMovement(FORWARD);
        moveForward(200);
        delay(200);
        
        animateEyesForMovement(BACKWARD);
        moveBackward(200);
        delay(200);
    }
    
    // Spin with excited eyes
    for (int i = 0; i < 5; i++) {
        left_eye_height = ref_eye_height + 5;
        right_eye_height = ref_eye_height + 5;
        draw_eyes();
        delay(100);
        left_eye_height = ref_eye_height;
        right_eye_height = ref_eye_height;
        draw_eyes();
        delay(100);
    }
    
    animateEyesForMovement(LEFT);
    moveLeft(1000);
    delay(1000);
    
    // Final animation
    stopMovement();
    happy_eye();
}

void setup() {
  Serial.begin(115200);
  Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2);
  
  // Initialize OLED display
  if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); // Don't proceed, loop forever
  }
  
  // Show initial display buffer contents on the screen
  display.display();
  delay(1000);
  
  // Motor pins setup (removed ENA and ENB)
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  stopMotors();  // Make sure motors are stopped initially

  // Show boot screen
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(15, 10);
  display.println("Booting");
  display.setCursor(30, 35);
  display.println("Nuki");
  display.display();
  delay(1000);

  display.clearDisplay();
  display.setCursor(25, 5);
  display.setTextSize(1);
  display.println("Booting...");
  display.display();

  int barWidth = 80;
  int x = (SCREEN_WIDTH - barWidth) / 2;
  int y = 30;
  for (int i = 0; i <= barWidth; i += 8) {
    display.drawRect(x, y, barWidth, 10, SSD1306_WHITE);
    display.fillRect(x, y, i, 10, SSD1306_WHITE);
    display.display();
    delay(100);
  }

  // Connect to WiFi
  if (!WiFi.config(local_IP, gateway, subnet, primaryDNS, secondaryDNS)) {
    Serial.println("STA Failed to configure");
  }

  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected.");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  server.begin();
  
  delay(300);
  display.clearDisplay();
  sleep();
  delay(2000);
}

void loop() {
  // Handle eye animations
  if (demo_mode == 1) {
    launch_animation_with_index(current_animation_index++);
    if (current_animation_index > max_animation_index) {
      current_animation_index = 0;
    }
  }

  // Handle web server requests
  WiFiClient client = server.available();
  if (client) {
    Serial.println("Client connected.");

    String request = "";
    unsigned long timeout = millis() + 2000;
    while (client.connected() && millis() < timeout) {
      while (client.available()) {
        char c = client.read();
        request += c;
        if (request.endsWith("\r\n\r\n")) break;
        timeout = millis() + 2000;
      }
      if (request.endsWith("\r\n\r\n")) break;
      delay(1);
    }

    Serial.println("Request received:");
    Serial.println(request);

    // Parse command and optional duration parameter
    String path = parseRequestPath(request);
    Serial.print("Parsed path: ");
    Serial.println(path);

    String command = "";
    unsigned long duration = 0;
    int value = 0;

    if (path.length() > 0) {
      command = path.substring(0, 1);
      if (path.length() > 1) {
        String paramStr = path.substring(1);
        if (command == "M") { // Servo command format: M1:90
          int colonPos = paramStr.indexOf(':');
          if (colonPos != -1) {
            duration = paramStr.substring(0, colonPos).toInt();
            value = paramStr.substring(colonPos+1).toInt();
          }
        } else {
          duration = paramStr.toInt();
        }
      }
    }

    Serial.print("Command: ");
    Serial.print(command);
    Serial.print(" Duration: ");
    Serial.print(duration);
    if (command == "M") {
      Serial.print(" Value: ");
      Serial.print(value);
    }
    Serial.println();

    bool validMoveCommand = false;

    if (command == "A") {
      // Animation commands (0-8)
      demo_mode = 0;
      int anim = path.substring(1).toInt();
      launch_animation_with_index(anim);
    } 
    else if (command == "S") {
      demo_mode = 0;
      sad_eye();
    }
    else if (command == "U") {
      demo_mode = 0;
      surprised_eye();
    }
    else if (command == "G") {
      demo_mode = 0;
      angry_eye();
    }
    else if (command == "W") {
      demo_mode = 0;
      wink_left_eye();
    }
    else if (command == "H") {
      demo_mode = 0;
      loveEyes();
    }
    else if (command == "R") {
      demo_mode = 1;
    }
    else if (command == "M") {
      int servoNum = path.substring(1, path.indexOf(":")).toInt();
      int queryIndex = request.indexOf("angle=");
      if (queryIndex != -1) {
        int angle = request.substring(queryIndex + 6).toInt(); // Get value after "angle="
        if (angle >= 0 && angle <= 180 && servoNum >= 1 && servoNum <= 3) {
          String servoCmd = "M" + String(servoNum) + ":" + String(angle);
          Serial2.print(servoCmd + "\n");
          delay(20);
          Serial.print("Sent to Arduino: ");
          Serial.println(servoCmd);
        } else {
          Serial.println("Invalid servo number or angle");
        }
      } else {
        Serial.println("No angle found in query.");
      }
    }
    else if (command == "C") {  // Action commands
      if (path == "C1") {
        Serial2.print("ACT1\n");
        Serial.println("Sent ACT1 to Arduino");
      } else if (path == "C2") {
        Serial2.print("ACT2\n");
        Serial.println("Sent ACT2 to Arduino");
      } else if (path == "C3") {
        Serial2.print("ACT3\n");
        Serial.println("Sent ACT3 to Arduino");
      } else if (path == "C4") {
        Serial2.print("ACT4\n");
        Serial.println("Sent ACT4 to Arduino");
      } else if (path == "C5") {
        Serial2.print("ACT5\n");
        Serial.println("Sent ACT5 to Arduino");
      }
      // New predefined movement commands
      else if (path == "C6") {
        moveAround();
      } else if (path == "C7") {
        figureEight();
      } else if (path == "C8") {
        cautiousExplore();
      } else if (path == "C9") {
        dance();
      }
    }
    else {
      // Movement commands: F, B, L, D, T
      if (command == "F") {
        animateEyesForMovement(FORWARD);
        moveForward(duration);
        validMoveCommand = true;
      } else if (command == "B") {
        animateEyesForMovement(BACKWARD);
        moveBackward(duration);
        validMoveCommand = true;
      } else if (command == "L") {
        animateEyesForMovement(LEFT);
        moveLeft(duration);
        validMoveCommand = true;
      } else if (command == "D") {
        animateEyesForMovement(RIGHT);
        moveRight(duration);
        validMoveCommand = true;
      } else if (command == "T") {
        stopMovement();
        animateEyesForMovement(NONE);
        validMoveCommand = true;
      }
    }

    // Send response HTML
    client.println("HTTP/1.1 200 OK");
    client.println("Content-type:text/html\r\n");
    client.println("<!DOCTYPE html><html><head><title>Eye Control & Robot Move</title>");
    client.println("<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">");
    client.println("<style>");
    client.println("body { font-family: Arial, sans-serif; margin: 20px; }");
    client.println("button { padding: 10px 15px; margin: 5px; font-size: 16px; }");
    client.println(".container { display: flex; flex-wrap: wrap; }");
    client.println(".section { margin: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }");
    client.println("</style></head><body>");
    
    client.println("<h1>Robot Control Panel</h1>");
    client.println("<div class=\"container\">");
    
    // Animation section
    client.println("<div class=\"section\">");
    client.println("<h2>Eye Animations</h2>");
    for (int i = 0; i <= 8; i++) {
      client.printf("<a href=\"/A%d\"><button>Anim %d</button></a>", i, i);
    }
    client.println("</div>");
    
    // Emotions section
    client.println("<div class=\"section\">");
    client.println("<h2>Eye Emotions</h2>");
    client.println("<a href=\"/S\"><button>Sad</button></a>");
    client.println("<a href=\"/U\"><button>Surprised</button></a>");
    client.println("<a href=\"/G\"><button>Angry</button></a>");
    client.println("<a href=\"/W\"><button>Wink</button></a>");
    client.println("<a href=\"/H\"><button>Love</button></a>");
    client.println("<a href=\"/R\"><button>Resume Demo</button></a>");
    client.println("</div>");
    
    // Movement section
    client.println("<div class=\"section\">");
    client.println("<h2>Robot Movement</h2>");
    client.println("<a href=\"/F1000\"><button>Forward 1s</button></a>");
    client.println("<a href=\"/B1000\"><button>Backward 1s</button></a>");
    client.println("<a href=\"/L1000\"><button>Left 1s</button></a>");
    client.println("<a href=\"/D1000\"><button>Right 1s</button></a>");
    client.println("<a href=\"/T\"><button>Stop</button></a>");
    client.println("</div>");
    
    // Servo control section
    client.println("<div class=\"section\">");
    client.println("<h2>Servo Control</h2>");
    client.println("<form action=\"/M1\" method=\"get\">");
    client.println("Servo 1 (0-180): <input type=\"number\" name=\"angle\" min=\"0\" max=\"180\" value=\"90\">");
    client.println("<input type=\"submit\" value=\"Move\">");
    client.println("</form>");
    
    client.println("<form action=\"/M2\" method=\"get\">");
    client.println("Servo 2 (0-180): <input type=\"number\" name=\"angle\" min=\"0\" max=\"180\" value=\"90\">");
    client.println("<input type=\"submit\" value=\"Move\">");
    client.println("</form>");
    
    client.println("<form action=\"/M3\" method=\"get\">");
    client.println("Servo 3 (0-180): <input type=\"number\" name=\"angle\" min=\"0\" max=\"180\" value=\"90\">");
    client.println("<input type=\"submit\" value=\"Move\">");
    client.println("</form>");
    client.println("</div>");
    
    // Actions section
    client.println("<div class=\"section\">");
    client.println("<h2>Servo Actions</h2>");
    client.println("<a href=\"/C1\"><button>Wave Right Hand</button></a>");
    client.println("<a href=\"/C2\"><button>Nod Head Yes</button></a>");
    client.println("<a href=\"/C3\"><button>Shake Head No</button></a>");
    client.println("<a href=\"/C4\"><button>Raise Both Hands</button></a>");
    client.println("<a href=\"/C5\"><button>Reset to Neutral</button></a>");
    client.println("</div>");
    
    // New predefined movements section
    client.println("<div class=\"section\">");
    client.println("<h2>Predefined Movements</h2>");
    client.println("<a href=\"/C6\"><button>Move Around</button></a>");
    client.println("<a href=\"/C7\"><button>Figure Eight</button></a>");
    client.println("<a href=\"/C8\"><button>Cautious Explore</button></a>");
    client.println("<a href=\"/C9\"><button>Dance</button></a>");
    client.println("</div>");
    
    client.println("</div>"); // Close container
    client.println("</body></html>");
    client.stop();
    Serial.println("Client disconnected.");
  }

  // Handle movement timing
  if (moving && moveDuration > 0) {
    if (millis() - moveStartTime >= moveDuration) {
      stopMovement();
      animateEyesForMovement(NONE);
      Serial.println("Movement stopped automatically after duration.");
    }
  }
}

String parseRequestPath(String request) {
  // Extract the path after "GET " and before first space or ?
  int start = request.indexOf("GET ");
  if (start == -1) return "";
  start += 4; // skip "GET "
  int end = request.indexOf(' ', start);
  if (end == -1) end = request.indexOf('?', start);
  if (end == -1) return "";
  String path = request.substring(start, end);
  if (path.length() > 0 && path[0] == '/') {
    path = path.substring(1); // Remove leading '/'
  }
  return path;
}

// Movement functions with duration parameter
void moveForward(unsigned long duration) {
  Serial.println("Moving forward");
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  startMovement(FORWARD, duration);
}

void moveBackward(unsigned long duration) {
  Serial.println("Moving backward");
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  startMovement(BACKWARD, duration);
}

void moveLeft(unsigned long duration) {
  Serial.println("Turning left");
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  startMovement(LEFT, duration);
}

void moveRight(unsigned long duration) {
  Serial.println("Turning right");
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  startMovement(RIGHT, duration);
}

void stopMotors() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}

void startMovement(MoveDirection dir, unsigned long duration) {
  currentMove = dir;
  moveStartTime = millis();
  moveDuration = duration;
  moving = true;

  Serial.print("Started move: ");
  Serial.print(dir);
  Serial.print(" for duration: ");
  Serial.println(duration);
}

void stopMovement() {
  stopMotors();
  moving = false;
  currentMove = NONE;
  moveDuration = 0;
  Serial.println("Movement stopped.");
}