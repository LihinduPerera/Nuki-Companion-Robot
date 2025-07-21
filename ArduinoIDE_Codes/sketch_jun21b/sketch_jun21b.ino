#include <WiFi.h>

#define RXD2 16
#define TXD2 17

// Motor pins for L298N
#define IN1 25
#define IN2 26
#define IN3 27
#define IN4 14

const char* ssid = "MT20_MIFI_GEN-66";
const char* password = "9g8P604?";

WiFiServer server(80);

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

void setup() {
  Serial.begin(115200);
  Serial2.begin(115200, SERIAL_8N1, RXD2, TXD2);
  delay(1000);
  Serial.println("ESP32 ready");

  // Motor pins setup
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  stopMotors();  // Make sure motors are stopped initially

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
}

void loop() {
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
    // Example URL: /F1000  means forward for 1000 ms
    String path = parseRequestPath(request);
    Serial.print("Parsed path: ");
    Serial.println(path);

    String command = "";
    unsigned long duration = 0;

    if (path.length() > 0) {
      command = path.substring(0, 1);
      if (path.length() > 1) {
        String durStr = path.substring(1);
        duration = durStr.toInt();
      }
    }

    Serial.print("Command: ");
    Serial.print(command);
    Serial.print(" Duration: ");
    Serial.println(duration);

    bool validMoveCommand = false;

    if (command == "A") {
      // Animation commands (0-8)
      Serial2.print(path + "\n");
    } 
    else if (command == "S" || command == "U" || command == "G" || command == "W" || command == "R") {
      // Emotions and resume demo
      Serial2.print(command + "\n");
    } 
    else {
      // Movement commands: F, B, L, D, T
      if (command == "F") {
        moveForward(duration);
        validMoveCommand = true;
      } else if (command == "B") {
        moveBackward(duration);
        validMoveCommand = true;
      } else if (command == "L") {
        moveLeft(duration);
        validMoveCommand = true;
      } else if (command == "D") {
        moveRight(duration);
        validMoveCommand = true;
      } else if (command == "T") {
        stopMovement();
        validMoveCommand = true;
      }
    }

    // Send response HTML
    client.println("HTTP/1.1 200 OK");
    client.println("Content-type:text/html\r\n");
    client.println("<!DOCTYPE html><html><head><title>Eye Control & Robot Move</title></head><body>");
    client.println("<h1>Choose Animation</h1>");
    for (int i = 0; i <= 8; i++) {
      client.printf("<a href=\"/A%d\"><button>Anim %d</button></a><br>", i, i);
    }
    client.println("<h2>Emotions</h2>");
    client.println("<a href=\"/S\"><button>Sad</button></a><br>");
    client.println("<a href=\"/U\"><button>Surprised</button></a><br>");
    client.println("<a href=\"/G\"><button>Angry</button></a><br>");
    client.println("<a href=\"/W\"><button>Wink</button></a><br>");
    client.println("<a href=\"/R\"><button>Resume Demo</button></a><br>");
    client.println("<h2>Robot Movement</h2>");
    client.println("<a href=\"/F1000\"><button>Forward 1s</button></a><br>");
    client.println("<a href=\"/B1000\"><button>Backward 1s</button></a><br>");
    client.println("<a href=\"/L1000\"><button>Left 1s</button></a><br>");
    client.println("<a href=\"/D1000\"><button>Right 1s</button></a><br>");
    client.println("<a href=\"/T\"><button>Stop</button></a><br>");
    client.println("</body></html>");
    client.stop();
    Serial.println("Client disconnected.");
  }

  // Handle movement timing
  if (moving && moveDuration > 0) {
    if (millis() - moveStartTime >= moveDuration) {
      stopMovement();
      Serial.println("Movement stopped automatically after duration.");
    }
  }
}

String parseRequestPath(String request) {
  // Extract the path after "GET " and before first space
  int start = request.indexOf("GET ");
  if (start == -1) return "";
  start += 4; // skip "GET "
  int end = request.indexOf(' ', start);
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
