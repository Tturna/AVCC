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

char ssid[] = "mokkula_482925";
char pass[] = "HN7MEF63FJD";
//char ssid[] = "TP-Link_2946";
//char pass[] = "64795164";
//char ssid[] = "uusikyla";
//char pass[] = "painuhiiteen";
char hostName[] = "192.168.8.109";
int port = 9999;
int status = WL_IDLE_STATUS;     // the Wifi radio's status

WiFiClient client;

bool gotReply = false;
  
float xAcc, yAcc, zAcc;
float xGyro, yGyro, zGyro;
float roll, pitch, yaw;

void setup() {
  if (!IMU.begin()) {
    while (1);
  }

  filter.begin(sensorRate);

  // check for the WiFi module:
  if (WiFi.status() == WL_NO_MODULE) {
    // don't continue
    while (true);
  }

  // attempt to connect to Wifi network:
  while (status != WL_CONNECTED) {
    // Connect to WPA/WPA2 network:
    status = WiFi.begin(ssid, pass);

    // wait 10 seconds for connection:
    delay(10000);
  }

  while (!client.connected())
  {
    if (client.connect(hostName, port)) {
      delay(5000);
    }
    else
    {
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

    client.print('y');
    client.print(pitchFiltered);
    client.print('p');
    client.print(roll);
    client.print('r');
    client.print(yaw);
  }

  //delay(15);  
}
