#include "pidclass.h"
#include "Arduino.h"

#define writePin 23
#define readPin 4
#define LED 2




//Define variables for PID
double Kp = 0.0127;
double Ki = 0.00965;
double Kd = 0.0000487;
double setPoint = 1.7;
double maxOutput = 3.3;

//Variables for timer
uint16_t input_bits, output_bits;
double input;
double output;
uint32_t startTime;

int count = 0;
const int maxCount = 10240;

//Define constants:
byte outputByteArray[2*maxCount]; //Voltage that have been measured out of the interferometer.
byte inputByteArray[2*maxCount];
byte timeByteArray[4*maxCount];

//Define variables for savind and sending. 
byte HighByte, MedHighByte, MedLowByte, LowByte;

PIDController pid(Kp, Ki, Kd);  // Create a PID controller object with specified gains

hw_timer_t *Timer0_Cfg = NULL; //Create a timer configuration

void IRAM_ATTR Timer0_ISR() //Interrupt function when timer is at 1ms. 
{
  uint32_t currentTime;
  input_bits = analogRead(readPin);    // Read input value in bits
  input = ((int)input_bits)*3.3/4095;
  output = pid.compute(input)*4095/3.3;
  output_bits = static_cast<uint16_t>(round(output));// Compute PID control signal
  analogWrite(writePin, output_bits);
  if(count<maxCount){
      //Put the voltage in 2 bytes and put it in the voltage array to send
      HighByte = (input_bits>>8) & 0xFF;
      LowByte = input_bits & 0xFF;
      //Create data array with measured data to send via uart
      outputByteArray[2*count] = HighByte;
      outputByteArray[1+2*count] = LowByte;

      //Put the voltage in 2 bytes and put it in the voltage array to send
      HighByte = (output_bits>>8) & 0xFF;
      LowByte = output_bits & 0xFF;
      //Create data array with calculted data to send via uart
      inputByteArray[2*count] = HighByte;
      inputByteArray[1+2*count] = LowByte;
      
      //Put the timestamp in 4 bytes and put in the time array to send
      currentTime = millis();
      HighByte = (currentTime-startTime>>24) & 0xFF;
      MedHighByte = (currentTime-startTime>>16) & 0xFF;
      MedLowByte = (currentTime-startTime>>8) & 0xFF;
      LowByte = (currentTime-startTime) & 0xFF;
      //Create timestamp array to send
      timeByteArray[4*count] = HighByte;
      timeByteArray[1+4*count] = MedHighByte;
      timeByteArray[2+4*count] = MedLowByte;
      timeByteArray[3+4*count] = LowByte;
  }
  count++; 
}

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

void setup() {
  //Set the PID controller setpoint in 12 bit.
  pid.setSetpoint(setPoint);

  //Set the PID controller maximum output as 3.3V
  pid.setMaxOutput(maxOutput);
  
  //Set the write resolution off the pwm signal to 12 bit(same as read default)
  analogWriteResolution(12);
  
  //open serial communications on baud rate 115200
  Serial.begin(115200);
  
  //Perform a check with the pc if they can send and receive
  startupCheck();
  
  //define start time for timestamps. 
  startTime = millis(); 
  
  //Interrupt timer for every 1ms. 
  Timer0_Cfg = timerBegin(0, 80, true); //1Mhz
  timerAttachInterrupt(Timer0_Cfg, &Timer0_ISR, true);
  timerAlarmWrite(Timer0_Cfg, 1000, true); //counts to 1000 -> 1Khz = 1ms
  timerAlarmEnable(Timer0_Cfg); //Enable interupt
}

void loop() {
  if(count == maxCount){
    //Send arrays
  Serial.write(outputByteArray,2*maxCount);
  Serial.write(inputByteArray,2*maxCount);
  Serial.write(timeByteArray,4*maxCount);
  }

}
