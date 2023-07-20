#include <Arduino_LSM6DS3.h>
#include <WiFiNINA.h>
#include <MadgwickAHRS.h>
#include <Math.h>

float pitchFilteredOld;
Madgwick filter;
const float sensorRate = 104.00;

//char ssid[] = "mokkula_482925";
//char pass[] = "HN7MEF63FJD";
char ssid[] = "uusikyla";
char pass[] = "painuhiiteen";
char hostName[] = "192.168.1.92";
int port = 9999;
int status = WL_IDLE_STATUS;     // the Wifi radio's status

WiFiClient client;

bool gotReply = false;

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
    client.connect(hostName, port);
    delay(5000);
  }
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
    pitchFilteredOld = pitchFiltered;

    client.print(pitchFiltered);
  }
}