#include <Arduino.h>
#include <stdio.h>

#define CURRENT_PIN A0
#define VOLTAGE_PIN A1
#define PWM_PIN 10
#define LED_PIN 13
#define DT_PIN  3
#define SCK_PIN 4

#define PWM_MAX   200 // up to 255
#define PWM_STEP  10

char str[40];

uint32_t hx711GetValue()
{
  uint32_t result = 0;
  uint8_t i = 0;
  while (digitalRead(DT_PIN)) {};
  for (i = 0; i < 24; i++) {
    result <<= 1;
    digitalWrite(SCK_PIN, 1);
    delayMicroseconds(5);
    result |= digitalRead(DT_PIN);
    digitalWrite(SCK_PIN, 0);
    delayMicroseconds(5);
  }
  digitalWrite(SCK_PIN, 1);
  delayMicroseconds(5);
  digitalWrite(SCK_PIN, 0);
  delayMicroseconds(5);

  return result;
}

void setup() 
{
  pinMode(PWM_PIN, OUTPUT);
  pinMode(DT_PIN, INPUT);
  pinMode(SCK_PIN, OUTPUT);
  TCCR1B &= ~0x07; // Clear PWM clock divider 
  TCCR1B |= 0x02; // Set PWM clock divider to 8 
  Serial.begin(115200);
}

void loop() 
{
  uint8_t cmdByte = 0;
  while (cmdByte != 'S')
    if (Serial.available() > 0)
      cmdByte = Serial.read();
  for (uint8_t pwm = 0; pwm < PWM_MAX; pwm+=PWM_STEP) {
    analogWrite(PWM_PIN, pwm);
    digitalWrite(LED_PIN, HIGH);
    delay(200);
    digitalWrite(LED_PIN, LOW);
    hx711GetValue(); // Dummy read
    for (uint8_t i = 0; i < 10; i++) {
      uint16_t voltage = analogRead(VOLTAGE_PIN);
      uint16_t current = analogRead(CURRENT_PIN);
      uint32_t pull = hx711GetValue()>>4;
      sprintf(str, "%d\t%d\t%d\t%d\n", pwm, voltage, current, pull);
      Serial.print(str);
    }
  }
  analogWrite(PWM_PIN, 0);
  Serial.println("Done");
}
