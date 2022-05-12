#include <Arduino_LSM6DS3.h>
#undef max
#undef min
#include <SPI.h>
#include <WiFiNINA.h>
#include <MadgwickAHRS.h>
#include <Math.h>
//#include <iostream>

float pitchFilteredOld;
Madgwick filter;
const float sensorRate = 104.00;

//#include "arduino_secrets.h" 
///////please enter your sensitive data in the Secret tab/arduino_secrets.h
//char ssid[] = SECRET_SSID;        // your network SSID (name)
//char pass[] = SECRET_PASS;    // your network password (use for WPA, or use as key for WEP)

char ssid[] = "mokkula_482925";
char pass[] = "HN7MEF63FJD";
char hostName[] = "192.168.8.112";
int port = 9999;
int status = WL_IDLE_STATUS;     // the Wifi radio's status

WiFiClient client;

bool gotReply = false;

void setup() {
  Serial.begin(9600);
  while (!Serial);

  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");

    while (1);
  }

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

  Serial.print("\nGyro");
  Serial.print("Gyroscope sample rate = ");
  Serial.print(IMU.gyroscopeSampleRate());
  Serial.println(" Hz");
  Serial.println();
  Serial.println("Gyroscope in degrees/second");
  Serial.println("X\tY\tZ");

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
  
  float xAcc, yAcc, zAcc;
  float xGyro, yGyro, zGyro;
  float roll, pitch, heading;
  if(IMU.accelerationAvailable() && IMU.gyroscopeAvailable()){
    IMU.readAcceleration(xAcc, yAcc, zAcc);
    IMU.readGyroscope(xGyro, yGyro, zGyro); 
    filter.updateIMU(xGyro, yGyro, zGyro, xAcc, yAcc, zAcc);
    pitch = filter.getPitch();
    float pitchFiltered = 0.1 * pitch + 0.9 * pitchFilteredOld; // low pass filter
    Serial.println("pitch: " + String(pitchFiltered));
    pitchFilteredOld = pitchFiltered;

    client.print(pitchFiltered);

    //client.print("g");
    //client.print(gx);
    //client.print(",");
    //client.print(gy);
    //client.print(",");
    //client.print(gz);
    //client.print("a");
    //client.print(ax);
    //client.print(",");
    //client.print(ay);
    //client.print(",");
    //client.print(az);
    //client.print("e");
  }

  //delay(100);  
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
