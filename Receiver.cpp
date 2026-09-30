#include <ESP8266WiFi.h> 
#include <LoRa.h> 
#include <ArduinoJson.h> // Include the ArduinoJson library 

#define LORA_SCK    D5 
#define LORA_MISO   D6 
#define LORA_MOSI   D7 
#define LORA_SS     D8 
#define LORA_RST    D2 
#define LORA_DIO0   D1
// RGB LED pins 
#define RED_PIN     D1 
#define GREEN_PIN   D2 
#define BLUE_PIN    D3 
 
// LoRa settings 
const long frequency = 868E6; // 868 MHz 
 
void setup() { 
  Serial.begin(115200); 
  while (!Serial); 
 
  // Initialize RGB LED pins 
  pinMode(RED_PIN, OUTPUT); 
  pinMode(GREEN_PIN, OUTPUT); 
  pinMode(BLUE_PIN, OUTPUT); 
 
  // Initialize LoRa 
  if (!LoRa.begin(frequency)) { 
    Serial.println("LoRa initialization failed. Check your 
connections."); 
    setLEDStatus("error"); 
    while (1); 
  } 
 
  // Set LoRa module pins 
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0); 
 
  Serial.println("LoRa Receiver Initialized."); 
  setLEDStatus("no_signal"); // Start with no signal 
} 
 
void loop() { 
  // Check if there is any data available to read 
  int packetSize = LoRa.parsePacket(); 
  if (packetSize) { 
    setLEDStatus("received"); // Signal received 
    Serial.print("Received packet of size "); 
    Serial.println(packetSize); 
 
    // Read packet 
    String receivedData = ""; 
    while (LoRa.available()) { 
      receivedData += (char)LoRa.read(); 
    } 
     
    Serial.print("Data: "); 
    Serial.println(receivedData); 
 
    // Parse JSON data 
    DynamicJsonDocument doc(1024); 
    DeserializationError error = deserializeJson(doc, receivedData); 
     
    if (!error) { 
 
45 
 
      // Extract and display fields for Serial Plotter 
      String time = doc["time"]; 
      int pzt1 = doc["PZT1"]; 
      int pzt2 = doc["PZT2"]; 
      int pzt3 = doc["PZT3"]; 
      int pzt4 = doc["PZT4"]; 
      float vibration = doc["vibration"]; 
 
      Serial.print("Time: "); 
      Serial.print(time); 
      Serial.print(", "); 
       
      Serial.print("PZT1: "); 
      Serial.print(pzt1); 
      Serial.print(", "); 
       
      Serial.print("PZT2: "); 
      Serial.print(pzt2); 
      Serial.print(", "); 
       
      Serial.print("PZT3: "); 
      Serial.print(pzt3); 
      Serial.print(", "); 
       
      Serial.print("PZT4: "); 
      Serial.print(pzt4); 
      Serial.print(", "); 
       
      Serial.print("Vibration: "); 
      Serial.println(vibration); 
    } else { 
      Serial.print("JSON deserialization failed: "); 
      Serial.println(error.c_str()); 
      setLEDStatus("error"); // Error occurred 
    } 
  } else { 
    setLEDStatus("no_signal"); // No signal 
  } 
 
  delay(1000); 
} 
 
// Function to control the RGB LED status 
void setLEDStatus(String status) { 
  // Turn off all LEDs 
  digitalWrite(RED_PIN, LOW); 
  digitalWrite(GREEN_PIN, LOW); 
  digitalWrite(BLUE_PIN, LOW); 
 
  if (status == "received") { 
    // Green LED 
    digitalWrite(GREEN_PIN, HIGH); 
  } else if (status == "no_signal") { 
    // Red LED 
    digitalWrite(RED_PIN, HIGH); 
 
46 
 
  } else if (status == "error") { 
    // Blue LED 
    digitalWrite(BLUE_PIN, HIGH); 
  } 
} 
 
