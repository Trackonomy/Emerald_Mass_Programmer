#include <Wire.h>
//#include <lp55231.h>
int iter = 15;

//Lp55231 ledChip;
//int LED_10 = 9;

int emags[15] = {2,3,4,5,6,7,8,9,10,11,12,14,15,16,17};
//int emags[4] = {13,14,15,16};
void setup() {
  Serial.begin(9600);
//  ledChip.Begin();
//  ledChip.Enable();
//  pinMode(LED_10, OUTPUT);
  for (int i = 0; i <= iter; i++) {
    pinMode(emags[i], OUTPUT);
  }
}


void loop() {
  if (Serial.available() > 0) {
    //String a = Serial.readString();
    char x = Serial.read();

    switch(x){
      case '0': 
      allOn(20000,0);
      allOff(0);
      break;

      case '1':
      for (int x=0; x <=3; x++) {
        allPulse(2000,0,0);
      }
      break;
      
      case '2':
      delay(15000);
      allOn(0,0);
      break;
  
      case '3':
      allOff(0);
      break;

      case '4':
      for (int x=0; x <=3; x++) {
        allPulse(1500,0,0);
      }
    }
  }
}


void allOn(int delay_time,int current) {
//  for (current; current<4; current++){
//    ledChip.SetChannelPWM(current, 255); //Turns on LED
//  }
//  digitalWrite(LED_10,HIGH);
  for (int i = 0; i <= iter; i++) {
    digitalWrite(emags[i], HIGH); //Turns all 10 magnets on
  }
  delay(delay_time); //delay to turn on magnets for atleast 10s to put them into DFU mode
}

void allOff (int previous){
  for (int i = 0; i <= iter; i++) {
    digitalWrite(emags[i], LOW);  //Turns all 10 magnets off
  }
//  digitalWrite(LED_10,LOW);
//  for (previous; previous <= 4; previous++) {
//    ledChip.SetChannelPWM(previous, 0); //Turns off LED
//  }
}

void allPulse(int delay_time, int current, int previous) {
//  for (current; current<4; current++){
//  ledChip.SetChannelPWM(current, 255); //Turns on LED
//  }
//  digitalWrite(LED_10,HIGH);
  for (int i = 0; i <= iter; i++) {
    digitalWrite(emags[i], HIGH); //Turns all 10 magnets on
  }
  delay(delay_time); //delay to turn on magnets for atleast 10s to put them into DFU mode
  for (int i = 0; i <= iter; i++) {
    digitalWrite(emags[i], LOW);  //Turns all 10 magnets off
  }
//  digitalWrite(LED_10,LOW);
//  for (previous; previous <= 4; previous++) {
//    ledChip.SetChannelPWM(previous, 0); //Turns off LED
//  }
  delay(delay_time);     
}
