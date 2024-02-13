#include <FastLED.h>
#include <ArduinoOSCWiFi.h>

#define NUM_LEDS 300
#define DATA_PIN 12
#define COLOR_ORDER GRB
#define CHIPSET WS2812B
#define BRIGHTNESS 255
#define VOLTS 5
#define MAX_AMPS 3000

CRGB leds[NUM_LEDS];

char* ssid = "avcc-ard";
char* pass = "avcc-intra-wlan";
char* host = "10.0.0.137";
int inPort = 9050;
const IPAddress ip(10, 0, 0, 70); // Arduino IPs 50-80
const IPAddress gateway(10, 0, 0, 1);
const IPAddress subnet(255, 255, 0, 0);

float r; float g; float b; float a;

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

  delay(1000);
  for (int i = 0; i < NUM_LEDS; i++)
  {
    leds[i] = CRGB::White;
  }
  FastLED.show();
}

int dir = 1;
int phase = 0;
float mul = 0;
float delayMs = 20;

void simpleWave()
{
  for (int c = 0; c < 3; c++)
  {
    CRGB color = CRGB(255, 0, 0);

    if (c == 1)
    {
      color = CRGB(0, 255, 0);
    }
    else if (c == 2)
    {
      color = CRGB(0, 0, 255);
    }

    for (int i = 0; i < NUM_LEDS; i++)
    {
      leds[i] = color;
      FastLED.show();
      delay(7);
    }
  }
}

void simpleRedFadein()
{
  for (int i = 0; i < NUM_LEDS; i++)
  {
    leds[i] = CRGB(255 * mul, 0, 0);
  }
  FastLED.show();

  mul += delayMs / 1000.0f;
  
  if (mul > 1)
  {
    mul = 0.0f;
  }

  delay(delayMs);
}

void rainbow()
{
  if (phase == 1)
  {
    r = 1 - mul;
    g = mul;
  }
  else if (phase == 2)
  {
    g = 1 - mul;
    b = mul;
  }
  else
  {
    b = 1 - mul;
    r = mul;
  }
  
  mul += delayMs / 1000.0f;

  if (mul > 1)
  {
    mul = 0.0f;
    phase = (phase + 1) % 3;
  }

  for (int i = 0; i < NUM_LEDS; i++)
  {
    leds[i] = CRGB(255 * r, 255 * g, 255 * b);
  }

  FastLED.show();
  delay(delayMs);
}

void thermometer()
{
  for (int i = 0; i < NUM_LEDS; i++)
  {
    if (i < a * NUM_LEDS)
    {
      leds[i] = CRGB(255 * max(0, (a - 0.5f) * 2), 255 * min(a, (1 - a)), 255 * max(0, 1 - a * 2));
    }
    else
    {
      leds[i] = CRGB::Black;
    }
  }
  FastLED.show();
  delay(10);
}

int width = 15;
void flickKitt()
{
  if (a <= 0) return;

  for (int i = 0; i < NUM_LEDS; i++)
  {
    float deltaCenter = abs(i - mul);
    float brightnessMul = 1.0f - max(0.1f, min(1, deltaCenter / floor(width / 2.0f)));

    if (i < mul + width / 2 && i > mul - width / 2)
    {
      leds[i] = CRGB(255 * brightnessMul, 0, 32 * (1.0f - brightnessMul));
    }
    else
    {
      leds[i] = CRGB::Black;
    }
  }
  mul += dir;

  if (mul == NUM_LEDS || mul == 0)
  {
    dir *= -1;
    a = 0;
  }

  FastLED.show();
  delay(1);
}

void updateColor()
{
  for (int i = 0; i < NUM_LEDS; i++)
  {
    leds[i] = CRGB(r * a * 255, g * a * 255, b * a * 255);
  }
  FastLED.show();
  delay(10);
}

void runners()
{
  for (int i = 0; i < NUM_LEDS; i++)
  {
    float normalizedIndex = (float)i / NUM_LEDS;
    float rNormalizedIndex = 1.0f - normalizedIndex;

    if (i == mul)
    {
      leds[i] = CRGB(255, 0, 255 * normalizedIndex);
    }
    else if (i == NUM_LEDS - mul)
    {
      leds[i] = CRGB(255, 0, 255 * rNormalizedIndex);
    }
    else if (i == (int)(floor(mul * 2)) % NUM_LEDS)
    {
      leds[i] = CRGB(0, 255 * normalizedIndex, 0);
    }
    else if (i == NUM_LEDS - (int)(floor(mul * 2)) % NUM_LEDS)
    {
      leds[i] = CRGB(0, 0, 255 * normalizedIndex);
    }
    else if (i == floor(mul / 2))
    {
      leds[i] = CRGB(255, 255, 0);
    }
    else if (i == NUM_LEDS - floor(mul / 2))
    {
      leds[i] = CRGB(255, 255, 0);
    }
    else
    {
      leds[i] = CRGB::Black;
    }
  }

  mul += dir;

  if (mul == NUM_LEDS || mul == 0)
  {
    dir *= -1;
  }

  FastLED.show();
}

void impact()
{
  if (a != 1) 
  {
    return;
  }

  float rm = 1.0f - sqrt(1.0f - pow(mul - 1, 2));
  Serial.println(rm);
  for (int i = 0; i < NUM_LEDS; i++)
  {
    leds[i] = CRGB(255.0f * rm, 255.0f * rm, 255.0f * rm);
  }

  mul += 30 / 1000.0f;
  
  if (mul > 1)
  {
    a = 0;
    mul = 0.0f;
  }

  FastLED.show();
  delay(1);
}

void test()
{
  for (int i = 0; i < NUM_LEDS; i++)
  {
    // float fader = sin(mul);
    float x = ((int)floor(i + mul) % 40);
    float yf = 1.0f - x / 20;

    if (x < 20)
    {
      leds[i] = CRGB(r * 255, g * 255, b * 255);
    }
    // else if ((i % 20) >= 10)
    // {
    //   leds[i] = CRGB(255, 0, 128);
    // }
    else
    {
      // leds[i] = CRGB(32, 32, 32);
      leds[i] = CRGB(0, 0, 0);
    }
  }

  mul += 1;
  FastLED.show();

  delay(10);
}

void loop()
{
  // simpleWave();
  // simpleRedFadein();
  rainbow();
  // thermometer();
  // flickKitt();
  // runners();
  // impact();
  // test();

  // for (int i = 0; i < NUM_LEDS; i++)
  // {
  //   // float n = (float)i / NUM_LEDS;
  //   leds[i] = CRGB(255, 255, 255);
  // }

  // FastLED.show();
  // delay(200);

  //updateColor();

  OscWiFi.update();
}