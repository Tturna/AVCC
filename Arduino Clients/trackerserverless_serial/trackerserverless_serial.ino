#include <Arduino_LSM6DS3.h>
//#undef max
//#undef min
//#include <SPI.h>
//#include <WiFiNINA.h>
#include <ArduinoOSCWiFi.h>
#include <MadgwickAHRS.h>
#include <Math.h>
//#include <iostream>

Madgwick filter;
const float sensorRate = 52.00;
const float pitchSmooth = 1.0;
unsigned long microsPerReading, microsPrevious;

//#include "arduino_secrets.h" 
///////please enter your sensitive data in the Secret tab/arduino_secrets.h
//char ssid[] = SECRET_SSID;        // your network SSID (name)
//char pass[] = SECRET_PASS;    // your network password (use for WPA, or use as key for WEP)

//char* ssid = "mokkula_482925";
//char* pass = "HN7MEF63FJD";
//char ssid[] = "crumbs";
//char pass[] = "64795164";
//char* ssid = "uusikyla";
//char* pass = "painuhiiteen";
//char* ssid = "TP-Link_38DB";
//char* pass = "13452216";
char* ssid = "avcc-ard";
char* pass = "avcc-intra-wlan";

char* host = "192.168.2.100";
int port = 8001;
const IPAddress ip(192, 168, 2, 6);
const IPAddress gateway(192, 168, 2, 1);
const IPAddress subnet(255, 255, 255, 0);

//WiFiClient client;

bool gotReply = false;
  
float xAcc, yAcc, zAcc;
float xGyro, yGyro, zGyro;
float roll, pitch, yaw;
float pitchFilteredOld;

void setup() {
  Serial.begin(9600);
  while (!Serial);

  Serial.println(ssid);
  Serial.println(pass);

  Serial.print("IDLE STATUS: ");
  Serial.println(WL_IDLE_STATUS);
  Serial.print("NO SSID AVAIL: ");
  Serial.println(WL_NO_SSID_AVAIL);
  Serial.print("SCAN COMPLETED: ");
  Serial.println(WL_SCAN_COMPLETED);
  Serial.print("CONNECTED: ");
  Serial.println(WL_CONNECTED);
  Serial.print("CONNECT FAILED: ");
  Serial.println(WL_CONNECT_FAILED);
  Serial.print("DISCONNECTED: ");
  Serial.println(WL_DISCONNECTED);
  Serial.print("NO SHIELD: ");
  Serial.println(WL_NO_SHIELD);

  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }

  filter.begin(sensorRate);
  
  // initialize variables to pace updates to correct rate
  microsPerReading = 1000000 / sensorRate;
  microsPrevious = micros();

  // attempt to connect to Wifi network:
  WiFi.begin(ssid, pass);
  WiFi.config(ip, gateway, subnet);
  while (WiFi.status() != WL_CONNECTED) {
      Serial.print("Wifi status: ");
      Serial.println(WiFi.status());
      delay(500);
  }
  Serial.print("WiFi connected, IP = ");
  Serial.println(WiFi.localIP());

  // you're connected now, so print out the data:
  Serial.print("You're connected to the network");
  printCurrentNet();
  printWifiData();
  delay(2000);

  OscWiFi.publish(host, port, "/ard/2", pitchFilteredOld, roll, yaw, xAcc, yAcc, zAcc)
        ->setFrameRate(sensorRate);
}

void loop() {
  unsigned long microsNow;
  
  //if(IMU.accelerationAvailable() && IMU.gyroscopeAvailable())
  {
    
    // check if it's time to read data and update the filter
    microsNow = micros();
    
    if (microsNow - microsPrevious >= microsPerReading) {
      IMU.readAcceleration(xAcc, yAcc, zAcc);
      IMU.readGyroscope(xGyro, yGyro, zGyro); 
      filter.updateIMU(xGyro, yGyro, zGyro, xAcc, yAcc, zAcc);
      pitch = filter.getPitch();
      roll = filter.getRoll();
      yaw = filter.getYaw();
      float pitchFiltered = pitchSmooth * pitch + (1 - pitchSmooth) * pitchFilteredOld; // low pass filter
      pitchFilteredOld = pitchFiltered;
  
      Serial.println(pitchFiltered);
  
      OscWiFi.post();
      
      // increment previous time, so we keep proper pace
      microsPrevious = microsPrevious + microsPerReading;
    }
  }

  //delay(15);  
}

void printWifiData() {
  // print your board's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);
  Serial.println(ip);

  // print your MAC address:
  byte mac[6];
  WiFi.macAddress(mac);
  Serial.print("MAC address: ");
  printMacAddress(mac);
}

void printCurrentNet() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print the MAC address of the router you're attached to:
  byte bssid[6];
  WiFi.BSSID(bssid);
  Serial.print("BSSID: ");
  printMacAddress(bssid);

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.println(rssi);

  // print the encryption type:
  byte encryption = WiFi.encryptionType();
  Serial.print("Encryption Type:");
  Serial.println(encryption, HEX);
  Serial.println();
}

void printMacAddress(byte mac[]) {
  for (int i = 5; i >= 0; i--) {
    if (mac[i] < 16) {
      Serial.print("0");
    }
    Serial.print(mac[i], HEX);
    if (i > 0) {
      Serial.print(":");
    }
  }
  Serial.println();
}
