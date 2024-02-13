#include <Arduino_LSM6DS3.h>
#include <ArduinoOSCWiFi.h>
#include <MadgwickAHRS.h>
#include <Math.h>

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
char* ssid = "avcc-ard";
char* pass = "avcc-intra-wlan";
char* host = "10.0.0.137";
int port = 8000;
const IPAddress ip(10, 0, 0, 58); // Arduino IPs 50-80
const IPAddress gateway(10, 0, 0, 1);
const IPAddress subnet(255, 255, 0, 0);

bool gotReply = false;
  
float xAcc, yAcc, zAcc;
float xGyro, yGyro, zGyro;
float roll, pitch, yaw;
float pitchFilteredOld;

void setup() {
  //Serial.begin(9600);
  //while (!Serial);

  if (!IMU.begin()) {
    //Serial.println("Failed to initialize IMU!");
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
      //Serial.print(".");
      delay(500);
  }
  //Serial.print("WiFi connected, IP = ");
  //Serial.println(WiFi.localIP());

  // you're connected now, so print out the data:
  //Serial.print("You're connected to the network");
  //printCurrentNet();
  //printWifiData();
  delay(2000);

  OscWiFi.publish(host, port, "/ard/8", pitchFilteredOld, roll, yaw, xAcc, yAcc, zAcc)
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
  
      //Serial.println(pitchFiltered);
  
      OscWiFi.post();
      
      // increment previous time, so we keep proper pace
      microsPrevious = microsPrevious + microsPerReading;
    }
  }
}
