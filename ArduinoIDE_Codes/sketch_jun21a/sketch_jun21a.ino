#include <SoftwareSerial.h>
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET     -1
#define SCREEN_ADDRESS 0x3C

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

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

// NEW EMOTIONS:

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

SoftwareSerial espSerial(8, 9); // RX, TX from ESP32

void setup() {
  display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS);
  Serial.begin(115200);
  espSerial.begin(115200);

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

  delay(300);
  display.clearDisplay();
  sleep();
  delay(2000);
}

void loop() {
  if (demo_mode == 1) {
    launch_animation_with_index(current_animation_index++);
    if (current_animation_index > max_animation_index) {
      current_animation_index = 0;
    }
  }

  if (espSerial.available()) {
    String data = espSerial.readStringUntil('\n');
    data.trim();
    char cmd = data[0];

    if (cmd == 'A') {
      demo_mode = 0;
      int anim = data.substring(1).toInt();
      launch_animation_with_index(anim);
      espSerial.println("Ran anim A" + String(anim));
    } else {
      demo_mode = 0;
      switch (cmd) {
        case 'S': sad_eye(); espSerial.println("Sad"); break;
        case 'U': surprised_eye(); espSerial.println("Surprised"); break;
        case 'G': angry_eye(); espSerial.println("Angry"); break;
        case 'W': wink_left_eye(); espSerial.println("Wink"); break;
        case 'R': demo_mode = 1; espSerial.println("Resume demo"); break;
        default: espSerial.println("Unknown command"); break;
      }
    }
  }
}
