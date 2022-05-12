#include <Wire.h>
#include <lp55231.h>
int iter = 10;

Lp55231 ledChip;
int LED_10 = 9;

int emags[10] = {15,14,16,4,6,7,2,5,3,8};
void setup() {
  Serial.begin(9600);
  ledChip.Begin();
  ledChip.Enable();
  pinMode(LED_10, OUTPUT);
  for (int i = 0; i <= 9; i++) {
    pinMode(emags[i], OUTPUT);
  }
}


void loop() {
  if (Serial.available() > 0) {
    char a = Serial.read();
    if(a == '1'){
      for (int x=0; x <=3; x++) {
        allPulse(1500,0,0);
      }
    }
  }
}

void allPulse(int delay_time, int current, int previous) {
  
  for (current; current<10; current++){
  ledChip.SetChannelPWM(current, 255); //Turns on LED
  }
  digitalWrite(LED_10,HIGH);
  for (int i = 0; i <= iter; i++) {
    digitalWrite(emags[i], HIGH); //Turns all 10 magnets on
  delay(delay_time); //delay to turn on magnets for atleast 10s to put them into DFU mode
  for (int i = 0; i <= iter; i++) {
    digitalWrite(emags[i], LOW);  //Turns all 10 magnets off
  }
  digitalWrite(LED_10,LOW);
  for (previous; previous <= iter; previous++) {
    ledChip.SetChannelPWM(previous, 0); //Turns off LED
  }
  delay(delay_time);   
}
