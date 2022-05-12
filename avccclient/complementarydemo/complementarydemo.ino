// Followed guide:
//

// This shit doesn't work

#include <Arduino_LSM6DS3.h>
#undef max
#undef min

//const float M_PI = 3.14159265359f;
float pitch, roll;

void setup() {
  Serial.begin(9600);
  while (!Serial);

  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");

    while (1);
  }

  Serial.print("\nGyro");
  Serial.print("Gyroscope sample rate = ");
  Serial.print(IMU.gyroscopeSampleRate());
  Serial.println(" Hz");
  Serial.println();

  Serial.print("\nAcc");
  Serial.print("Accelerometer sample rate = ");
  Serial.print(IMU.accelerationSampleRate());
  Serial.println(" Hz");
  Serial.println();
  
  //Serial.println("Gyroscope in degrees/second");
  //Serial.println("X\tY\tZ");
}

void loop() {
  // Get IMU data
  
  float gx, gy, gz;
  float ax, ay, az;

  if (IMU.gyroscopeAvailable() && IMU.accelerationAvailable()) {
    IMU.readGyroscope(gx, gy, gz); //Get gyro values
    IMU.readAcceleration(ax, ay, az); // Get acceleration values

    Serial.print(gx);
    Serial.print('\t');
    Serial.print(gy);
    Serial.print('\t');
    Serial.print(gz);
    Serial.print('\t');
    Serial.print(ax);
    Serial.print('\t');
    Serial.print(ay);
    Serial.print('\t');
    Serial.print(az);
    Serial.print('\t');

    pitch += (gx / 70) * 104;
    roll += (gy / 70) * 104;

    int forceMagnitudeApprox = abs(ax + ay + az);
    if (forceMagnitudeApprox > 0.5f && forceMagnitudeApprox < 4) {
      float pitchAcc = atan2f(ay, az) * 180 / M_PI;
      pitch = pitch * 0.98 + pitchAcc * 0.02;

      float rollAcc = atan2f(ax, az) * 180 / M_PI;
      roll = roll * 0.98 + rollAcc * 0.02;
    }
    
    Serial.print(pitch);
    Serial.print('\t');
    Serial.println(roll);
  }
}
