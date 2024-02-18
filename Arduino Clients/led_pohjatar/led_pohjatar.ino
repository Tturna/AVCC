#include <FastLED.h>
#include <ArduinoOSCWiFi.h>
#include <fire.h>

#define NUM_LEDS 1200
#define DATA_PIN 12
#define COLOR_ORDER GRB
#define CHIPSET WS2812B
#define BRIGHTNESS 255
#define VOLTS 5
#define MAX_AMPS 8000

CRGB leds[NUM_LEDS];

char* ssid = "avcc-ard";
char* pass = "avcc-intra-wlan";
// char* host = "10.0.0.137";
// char* ssid = "uusikyla";
// char* pass = "painuhiiteen";
// char* host = "192.168.1.199";
int inPort = 9050;
const IPAddress ip(10, 0, 0, 70); // Arduino IPs 50-80
const IPAddress gateway(10, 0, 0, 1);
const IPAddress subnet(255, 255, 0, 0);
// const IPAddress ip(192, 168, 1, 51);
// const IPAddress gateway(192, 168, 1, 1);
// const IPAddress subnet(255, 255, 255, 0);

float r; float g; float b; float a; float mode;
float mul = 0;

void setup()
{
  // Serial.begin(9600);
  FastLED.addLeds<WS2812B, DATA_PIN, COLOR_ORDER>(leds, NUM_LEDS);
  FastLED.setMaxPowerInVoltsAndMilliamps(VOLTS, MAX_AMPS);
  FastLED.setBrightness(BRIGHTNESS);
  FastLED.clear();
  FastLED.show();

  WiFi.begin(ssid, pass);
  WiFi.config(ip, gateway, subnet);

  // subscribe osc packet and directly bind to variable
  OscWiFi.subscribe(inPort, "/led/rgb", r, g, b, a, mode);
  
  randomSeed(analogRead(0));

  delay(1000);
}

float lerp(float start, float end, float t) {
    // Ensure t is within the range [0, 255]
    // t = constrain(t, 0, 255);

    // Perform linear interpolation
    return start + (end - start) * t;
    // return ((end - start) * t) / 255 + start;
}

//ClassicFireEffect fire(NUM_LEDS, 30, 100, 3, 2, false, true);   // Outwards from Middle
//ClassicFireEffect fire(NUM_LEDS, 30, 100, 3, 2, true, true);    // Inwards toward Middle
//ClassicFireEffect fire(NUM_LEDS, 20, 100, 3, 4, true, false);     // Outwards from Zero
//ClassicFireEffect fire(NUM_LEDS, 20, 100, 3, 4, false, false);     // Inwards from End
ClassicFireEffect fire(NUM_LEDS, 30, 300, 30, 12, true, true);     // More Intense, Extra Sparking
//ClassicFireEffect fire(NUM_LEDS, 20, 100, 3, NUM_LEDS, true, false);     // Fan with correct rotation
void davesfire()
{
  // FastLED.clear();
  // fire.DrawFire();
  // FastLED.show();
  // delay(10);
}

void customfire()
{
  for (int i = 0; i < NUM_LEDS; i++)
  {
    int rg = random(64);
    int rw = random(196);
    
    if (rw == 1)
    {
      leds[i] = CRGB(255 * mul, 120 * mul, 80 * mul);
    }
    else
    {
      leds[i] = CRGB(255 * mul, (16 + rg) * mul, 0);
    }
  }
  FastLED.show();

  if (mul < 1)
  {
    mul += 0.005f;
    delay(20);
  }
  else
  {
    mul = 1.0f;
  }

  delay(20);
}

void whiteflash()
{
  while (true)
  {
    for (int i = 0; i < NUM_LEDS; i++)
    {
      leds[i] = CRGB(255.0 * mul, 255.0 * mul, 255.0 * mul);
    }
    FastLED.show();

    mul -= 0.075f;

    if (mul <= 0)
    {
      mul = 0.0f;
      return;
    }

    delay(10);
  }
}

void whiteflashfast()
{
  while (true)
  {
    for (int i = 0; i < NUM_LEDS; i++)
    {
      leds[i] = CRGB(255.0 * mul, 255.0 * mul, 255.0 * mul);
    }
    FastLED.show();

    mul -= 0.33f;

    if (mul <= 0)
    {
      mul = 0.0f;
      return;
    }

    delay(1);
  }
}

int flashLength = 60;
void doorflash()
{
  while (true)
  {
    float m = ((int)(mul * 100) % 10) / 10.0f;
    float br = 1.0f;
    for (int i = 0; i < flashLength; i++)
    {
      float halfLength = flashLength / 2.0f;
      if (i > halfLength)
      {
        br = ((halfLength / i) - 0.5f) * 2.0f;
      }

      leds[i] = CRGB(255 * m * br, 255 * m * br, 255 * m * br);
      leds[NUM_LEDS - i - 1] = CRGB(255 * m * br, 255 * m * br, 255 * m * br);
    }
    FastLED.show();

    mul -= 0.02f;

    if (mul <= 0)
    {
      mul = 0.0f;
      return;
    }

    delay(10);
  }
}

float targetBr = 0.0f;
float curBr = 0.0f;
void loisteputkifx()
{
  // if (abs(targetBr - curBr) < 0.02f)
  // {
  //   targetBr = random(100) / 100.0f;
  // }
  // else
  // {
  //   curBr = lerp(curBr, targetBr, 0.05f);
  // }

  // for (int i = 0; i < NUM_LEDS; i++)
  // {
  //   leds[i] = CRGB(255 * curBr, 255 * curBr, 255 * curBr);
  // }
  // FastLED.show();
  // delay(10);

  float m = (float)((int)(mul * 100) % 25) / 50.0f;
    for (int i = 0; i < NUM_LEDS; i++)
    {
      leds[i] = CRGB(255 * m, 255 * m, 255 * m);
    }
    FastLED.show();

    mul -= (0.04f + random(12) / 100.0f);

    if (mul <= 0.15f)
    {
      mul = 0.999f;
      delay(random(20) + 10);
      return;
    }

    delay(random(50) + 10);
}

void ghostfx()
{
  while (true)
  {
    float m = (float)((int)(mul * 100) % 25) / 50.0f;
    for (int i = 0; i < NUM_LEDS; i++)
    {
      leds[i] = CRGB(255 * r * m, 255 * g * m, 255 * b * m);
    }
    FastLED.show();

    mul -= 0.07f;

    if (mul <= 0)
    {
      mul = 0.0f;
      delay(100);
      return;
    }

    delay(20);
  }
}

void color()
{
  for (int i = 0; i < NUM_LEDS; i++)
  {
    leds[i] = CRGB(255 * r * a, 255 * g * a, 255 * b * a);
  }
  FastLED.show();
  delay(10);
}

void pohjatar()
{
  if (mode == 0.1f)
  {
    mul = 1.0f;
    mode = 0.0f;
    whiteflash();
  }
  else if (mode == 0.11f)
  {
    mul = 1.0f;
    mode = 0.0f;
    whiteflashfast();
  }
  else if (mode == 0.2f)
  {
    //davesfire();
    mul = 0.0f;
    mode = 0.21f;
    // customfire();
  }
  else if (mode == 0.21f)
  {
    customfire();
  }
  else if (mode == 0.3f)
  {
    // mul = 1.0f;
    // a = 0.0f;
    // doorflash();
    loisteputkifx();
  }
  else if (mode == 0.4f)
  {
    color();
  }
  else if (mode == 0.5f)
  {
    mul = 0.999f;
    mode = 0.4f;
    ghostfx();
  }
  else
  {
    FastLED.clear();
    FastLED.show();
    delay(10);
  }
}

void loop()
{
  pohjatar();
  // color();

  // for (int i = 0; i < NUM_LEDS; i++)
  // {
  //   leds[i] = CRGB(255, 0, 0);
  // }

  // FastLED.show();
  // delay(100);

  // Serial.println(a);
  OscWiFi.update();
}