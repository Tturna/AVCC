#include <FastLED.h>
#include <ArduinoOSCWiFi.h>
#include <fire.h>

#define NUM_LEDS 1200
#define DATA_PIN 12
#define COLOR_ORDER GRB
#define CHIPSET WS2812B
#define BRIGHTNESS 255
#define VOLTS 5
#define MAX_AMPS 500

CRGB leds[NUM_LEDS];

// char* ssid = "avcc-ard";
// char* pass = "avcc-intra-wlan";
//char* host = "10.0.0.137";
char* ssid = "uusikyla";
char* pass = "painuhiiteen";
char* host = "192.168.1.199";
int inPort = 9050;
// const IPAddress ip(10, 0, 0, 70); // Arduino IPs 50-80
// const IPAddress gateway(10, 0, 0, 1);
// const IPAddress subnet(255, 255, 0, 0);
const IPAddress ip(192, 168, 1, 51);
const IPAddress gateway(192, 168, 1, 1);
const IPAddress subnet(255, 255, 255, 0);

float r; float g; float b; float a;
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
  OscWiFi.subscribe(inPort, "/led/rgb", r, g, b, a);
  
  randomSeed(analogRead(0));

  delay(1000);
}

uint8_t lerp8(uint8_t start, uint8_t end, uint8_t t) {
    // Ensure t is within the range [0, 255]
    t = constrain(t, 0, 255);

    // Perform linear interpolation
    return ((end - start) * t) / 255 + start;
}

//ClassicFireEffect fire(NUM_LEDS, 30, 100, 3, 2, false, true);   // Outwards from Middle
//ClassicFireEffect fire(NUM_LEDS, 30, 100, 3, 2, true, true);    // Inwards toward Middle
//ClassicFireEffect fire(NUM_LEDS, 20, 100, 3, 4, true, false);     // Outwards from Zero
//ClassicFireEffect fire(NUM_LEDS, 20, 100, 3, 4, false, false);     // Inwards from End
ClassicFireEffect fire(NUM_LEDS, 30, 300, 30, 12, true, true);     // More Intense, Extra Sparking
//ClassicFireEffect fire(NUM_LEDS, 20, 100, 3, NUM_LEDS, true, false);     // Fan with correct rotation
void firefx()
{
  // FastLED.clear();
  // fire.DrawFire();
  // FastLED.show();
  // delay(10);
}

void test()
{
  for (int i = 0; i < NUM_LEDS; i++)
  {
    int rg = random(64);
    int rw = random(196);
    
    if (rw == 1)
    {
      leds[i] = CRGB(255, 160, 160);
    }
    else
    {
      leds[i] = CRGB(255, 16 + rg, 0);
    }
  }
  FastLED.show();
  delay(10);
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

    mul -= 0.15f;

    if (mul <= 0)
    {
      mul = 0.0f;
      return;
    }

    delay(10);
  }
}

void pohjatar()
{
  if (a == 0.1f)
  {
    mul = 1.0f;
    a = 0.0f;
    whiteflash();
  }
  else if (a == 0.2f)
  {
    firefx();
  }
  else
  {
    test();
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

void loop()
{
  // pohjatar();
  color();

  // for (int i = 0; i < NUM_LEDS; i++)
  // {
  //   leds[i] = CRGB(255, 0, 0);
  // }

  // FastLED.show();
  // delay(100);

  // Serial.println(a);
  OscWiFi.update();
}