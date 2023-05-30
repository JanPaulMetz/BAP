#define writePin 23
#define readPin 4
#define LED 2

uint16_t voltage[200];
int size = 200;

byte HighByte;
byte LowByte;

void startupCheck(){
    while (1)
    {
        //Delay to make sure serial does not overflow fast. 
        delay(100);
        // Read data from UART.
        int inByte = Serial.read();
        int outByte;
        
        if(inByte == 0x41){
            digitalWrite(LED, HIGH); //Put the blue LED(pin2) on
            outByte = 0x42;              //Send back confirmation for the start message. 
            Serial.write(outByte); //Send five times to make sure it reaches the pc. 
            break;
        }
    }
}

void sendSweep(uint16_t *voltage){
  int sweeps = 1;
  for (int i = 0; i < sweeps; i++){
    for (int j = 0; j < size; j++){
      
      analogWrite(writePin, j);
      delay(10);
      voltage[j+i*256] = analogRead(readPin);
    }
  }
}

void setup() {

  Serial.begin(115200);
  startupCheck();
  // put your setup code here, to run once:

  
    
}

void loop() {
  // put your main code here, to run repeatedly:
  sendSweep(voltage);
  delay(10);
  for(int i = 0; i < size; i++){
    HighByte = (voltage[i]>>8) & 0xFF;
    LowByte = voltage[i] & 0xFF;
    Serial.write(HighByte);
    Serial.write(LowByte);
    delay(10);
  }

}
