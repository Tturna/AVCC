int pins [12] = { 2,3,4,5,6,7,8,9,10,11,12,13};
int message [2];
int power = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT);

  for (int i = 0; i < 12; i++)
  {
    pinMode(pins[i], OUTPUT);
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available())
  {
    //int value = Serial.read();
    int val = Serial.read();

    if (val == 144 || val == 128)
    {
      message[0] = val;
      
      if (val == 144)
      {
        power = 1;
      }
      else
      {
        power = 0;
      }
    }
    else if (message[0] > 0)
    {
      if (val > 11)
      {
        return;
      }
      
      message[1] = val;

      Serial.print(message[0]);
      Serial.print(message[1]);
      Serial.print(power);
      
      //digitalWrite(LED_BUILTIN, HIGH);
      digitalWrite(pins[message[1]], power);
      //delay(500);
      //digitalWrite(LED_BUILTIN, LOW);
      //delay(500);



      //digitalWrite(pins[message[1]], power);
      //delay(500);
      //digitalWrite(pins[message[1]], power);

      message[0] = 0;
    }
  }
}
