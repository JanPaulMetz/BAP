#define writePin 23
#define readPin 4
#define LED 2


const int arraySize = 256;
uint16_t voltage[256];
const int sweeps = 5;

byte HighByte;
byte LowByte;

byte ByteArray [2*sweeps*arraySize];

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
  for (int j = 0; j < arraySize; j++){
    analogWrite(writePin, j);
    delay(1);
    voltage[j] = analogRead(readPin);
  }
  delay(10);
}

void readVoltage(){
  uint16_t volt = analogRead(readPin);
  HighByte = (volt>>8) & 0xFF;
  LowByte = volt & 0xFF;
  Serial.write(HighByte);
  Serial.write(LowByte);
}

void setup() {
  //open serial communications on baud rate 115200
  Serial.begin(115200);
  //Perform a check with the pc if they can send and receive
  startupCheck();
  
  for(int j = 0; j <sweeps; j++){
    sendSweep(voltage);
    for(int i = 0; i < arraySize; i++){
      HighByte = (voltage[i]>>8) & 0xFF;
      LowByte = voltage[i] & 0xFF;
      ByteArray[2*(i+arraySize*j)] = HighByte;
      ByteArray[1+2*(i+arraySize*j)] = LowByte;
      delay(1);
    }
  }
  Serial.write(ByteArray,2*sweeps*arraySize);
  
    
}

void loop() {
  // put your main code here, to run repeatedly:
//  sendSweep(voltage);
//  delay(10);
//  for(int i = 0; i < size; i++){
//    HighByte = (voltage[i]>>8) & 0xFF;
//    LowByte = voltage[i] & 0xFF;
//    Serial.write(HighByte);
//    Serial.write(LowByte);
//    delay(10);
//  }
//  readVoltage();
//  delay(1);

}
