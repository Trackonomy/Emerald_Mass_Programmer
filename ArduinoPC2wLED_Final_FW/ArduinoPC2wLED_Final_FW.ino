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
    if (a == '1') {
      allOn(20000,0);
      allOff(0);
    }
//    Serial.println(1);
//    char b = Serial.read();
//    if (b == '1'){
//      delay(10000);
//      allOff(0);
//    }
    char b = Serial.read();
    if(b == '1'){
      for (int x=0; x <=3; x++) {
        allPulse(2000,0,0);
      }
      delay(10000);
      allOn(0,0);
    }
    char c = Serial.read();{
      if(c == '1'){
        allOff(0);
      }
    }
  }
}


//=============


void allOn(int delay_time,int current) {
  //  if(millis() >= next){
  for (current; current<10; current++){
    ledChip.SetChannelPWM(current, 255); //Turns on LED
  }
  digitalWrite(LED_10,HIGH);
  for (int i = 0; i <= iter; i++) {
    digitalWrite(emags[i], HIGH); //Turns all 10 magnets on
  }
  delay(delay_time); //delay to turn on magnets for atleast 10s to put them into DFU mode
//  for (int i = 0; i <= iter; i++) {
//    digitalWrite(emags[i], LOW);  //Turns all 10 magnets off
//  }
//  digitalWrite(LED_10,LOW);
//  for (previous; previous <= iter; previous++) {
//    ledChip.SetChannelPWM(previous, 0); //Turns off LED
//  }
// delay(midDFU_delay); //delay to allow DFU to complete partially
//  for (current; current<10; current++){
//    ledChip.SetChannelPWM(current, 255); //Turns on LED
//  }
//  digitalWrite(LED_10,HIGH);
//  for (int i = 0; i <= iter; i++) {
//    digitalWrite(emags[i], HIGH); //Turns all 10 magnets on
//  }
//  Serial.println("off");
    //      previous = current;
    //      ledChip.SetChannelPWM(previous, 0); //Turns off LED
    //    }
    //  }
}
void allOff (int previous){
  for (int i = 0; i <= iter; i++) {
    digitalWrite(emags[i], LOW);  //Turns all 10 magnets off
  }
  digitalWrite(LED_10,LOW);
  for (previous; previous <= iter; previous++) {
    ledChip.SetChannelPWM(previous, 0); //Turns off LED
  }
}

void allPulse(int delay_time, int current, int previous) {
  for (current; current<10; current++){
  ledChip.SetChannelPWM(current, 255); //Turns on LED
  }
  digitalWrite(LED_10,HIGH);
  for (int i = 0; i <= iter; i++) {
    digitalWrite(emags[i], HIGH); //Turns all 10 magnets on
  }
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
//
//void allOff_1() {
////    delay(15000); //Wait for all 10 nodes to get DFU before turning magnets off to put them into sleep
//  digitalWrite(LED_10,HIGH);
//  for (static uint8_t current = 0; current<10; current++){
//  ledChip.SetChannelPWM(current, 255); //Turns on LED
//  }
//  for (int i = 0; i <= iter; i++) {
//    digitalWrite(emags[i], HIGH); //Turns on LED to put them into sleep
//    //    previous = current;
//  }
//  delay(15000);
//  for (int i = 0; i <= iter; i++) {
//    digitalWrite(emags[i], LOW);
//  }
//  digitalWrite(LED_10,LOW);
//  for (static uint8_t previous = 0; previous <= iter; previous++) {
//  ledChip.SetChannelPWM(previous, 0); //Turns off LED
//  }
//}
