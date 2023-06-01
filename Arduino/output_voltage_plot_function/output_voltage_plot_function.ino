#define writePin 23
#define readPin 4
#define LED 2

//Define constants:
const int arraySize = 256; //256-1 = 255 is 3.3V output
const int sweeps = 40;
byte ByteArray[2*sweeps*arraySize];
byte timeByteArray[4*sweeps*arraySize];




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

void sendSweep(uint16_t *voltage, uint32_t *timeStamps, int arraySize){
  for (int j = 0; j < arraySize; j++){
    analogWrite(writePin, j);
    delay(1); //Small delay to let it settle. 
    voltage[j] = analogRead(readPin);
    timeStamps[j] = millis();
  }
  delay(10); //Delay to let the voltage drop from 3.3V to 0V again. 
}

void readVoltage(){
  uint16_t volt = analogRead(readPin);
  byte HighByte, LowByte;
  HighByte = (volt>>8) & 0xFF;
  LowByte = volt & 0xFF;
  Serial.write(HighByte);
  Serial.write(LowByte);
}

void VoltageSweepRead(int arraySize, int sweeps){
  //Define constants and variables
  byte HighByte, MedHighByte, MedLowByte, LowByte;
  uint16_t voltage[arraySize];
  uint32_t timeStamps[arraySize];
//  byte* ByteArray = new byte[2*sweeps*arraySize];
//  byte* timeByteArray = new byte[4*sweeps*arraySize];
  //Define the starttime.
  uint32_t startTime = millis();
  //Loop to fill the bytearrays. 
  for(int j = 0; j <sweeps; j++){
    sendSweep(voltage, timeStamps, arraySize);
    for(int i = 0; i < arraySize; i++){
      //Put the voltage in 2 bytes and put it in the voltage array to send
      HighByte = (voltage[i]>>8) & 0xFF;
      LowByte = voltage[i] & 0xFF;
      //Create data array to send
      ByteArray[2*(i+arraySize*j)] = HighByte;
      ByteArray[1+2*(i+arraySize*j)] = LowByte;
      
      //Put the timestamp in 4 bytes and put in the time array to send
      HighByte = (timeStamps[i]-startTime>>24) & 0xFF;
      MedHighByte = (timeStamps[i]-startTime>>16) & 0xFF;
      MedLowByte = (timeStamps[i]-startTime>>8) & 0xFF;
      LowByte = (timeStamps[i]-startTime) & 0xFF;
      //Create timestamp array to send
      timeByteArray[4*(i+arraySize*j)] = HighByte;
      timeByteArray[1+4*(i+arraySize*j)] = MedHighByte;
      timeByteArray[2+4*(i+arraySize*j)] = MedLowByte;
      timeByteArray[3+4*(i+arraySize*j)] = LowByte;
    }
  }
}

void setup() {
  //open serial communications on baud rate 115200
  Serial.begin(115200);
  //Perform a check with the pc if they can send and receive
  startupCheck();
  VoltageSweepRead(arraySize, sweeps);
  //Serial.println("Calculated");
  Serial.write(ByteArray,2*sweeps*arraySize);
  Serial.write(timeByteArray,4*sweeps*arraySize);
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
