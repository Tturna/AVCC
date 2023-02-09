#include <Arduino_LSM6DS3.h>
//#undef max
//#undef min
//#include <SPI.h>
#include <WiFiNINA.h>
#include <MadgwickAHRS.h>
#include <Math.h>
//#include <iostream>

float pitchFilteredOld;
Madgwick filter;
const float sensorRate = 52.00;
const float pitchSmooth = 0.3;

//#include "arduino_secrets.h" 
///////please enter your sensitive data in the Secret tab/arduino_secrets.h
//char ssid[] = SECRET_SSID;        // your network SSID (name)
//char pass[] = SECRET_PASS;    // your network password (use for WPA, or use as key for WEP)

//char ssid[] = "mokkula_482925";
//char pass[] = "HN7MEF63FJD";
char ssid[] = "crumbs";
char pass[] = "64795164";
//char ssid[] = "uusikyla";
//char pass[] = "painuhiiteen";
char hostName[] = "192.168.1.103";
int port = 9999;
int status = WL_IDLE_STATUS;     // the Wifi radio's status

WiFiClient client;

bool gotReply = false;
  
float xAcc, yAcc, zAcc;
float xGyro, yGyro, zGyro;
float roll, pitch, yaw;

void setup() {
  Serial.begin(9600);
  while (!Serial);

  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }

  filter.begin(sensorRate);

  // check for the WiFi module:
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("Communication with WiFi module failed!");
    // don't continue
    while (true);
  }

  // attempt to connect to Wifi network:
  while (status != WL_CONNECTED) {
    Serial.print("Attempting to connect to WPA SSID: ");
    Serial.println(ssid);
    // Connect to WPA/WPA2 network:
    status = WiFi.begin(ssid, pass);

    // wait 10 seconds for connection:
    delay(10000);
  }

  // you're connected now, so print out the data:
  Serial.print("You're connected to the network");
  printCurrentNet();
  printWifiData();

  while (!client.connected())
  {
    Serial.print("Connecting to server: ");
    Serial.print(hostName);
    Serial.print(":");
    Serial.println(port);
    if (client.connect(hostName, port)) {
      Serial.println("connected");
      Serial.print("Waiting 5 seconds");
      delay(5000);
    }
    else
    {
      Serial.println("Failed to connect to server. Retrying...");
      delay(5000);
    }
  }

  /*
  while (true)
  {
    client.print(4343);
    delay(3000);
  }
  */
}

void loop() {
  if(IMU.accelerationAvailable() && IMU.gyroscopeAvailable()){
    IMU.readAcceleration(xAcc, yAcc, zAcc);
    IMU.readGyroscope(xGyro, yGyro, zGyro); 
    filter.updateIMU(xGyro, yGyro, zGyro, xAcc, yAcc, zAcc);
    pitch = filter.getPitch();
    roll = filter.getRoll();
    yaw = filter.getYaw();
    float pitchFiltered = pitchSmooth * pitch + (1 - pitchSmooth) * pitchFilteredOld; // low pass filter
    pitchFilteredOld = pitchFiltered;

    Serial.println(pitchFiltered);

    client.print('y');
    client.print(pitchFiltered);
    client.print('p');
    client.print(roll);
    client.print('r');
    client.print(yaw);
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
