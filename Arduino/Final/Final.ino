#include "pidclass.h"
#include "Arduino.h"

#define PWMpin 23
#define analogreadpin 4
#define LED 2


//Define constants for PID
double Kp = 0.0127;
double Ki = 0.00965;
double Kd = 0.0000487;
double setPoint = 1.7;
double maxOutput = 3.3;

//Variables for PID
uint16_t input_bits, output_bits;
double input;
double output;

TaskHandle_t Task1; //Create task to handle on certain core. 
hw_timer_t *Timer0_Cfg = NULL;  //Create timer. 

PIDController pid(Kp, Ki, Kd);  // Create a PID controller object with specified gains

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
            outByte = 0x42;               
            Serial.write(outByte);  //Send back confirmation for the start message.
            break;
        }
    }
}

int* lambda_calibration(int maximumOutVoltageBits){  //Function to calibrate the lambda control. 
  int* returnVoltages = new int[3];
  int voltage, maxVoltage = 0; //Set lowest value possible so it always goes up. 
  int maximumOutVoltageInBits = pow(2, maximumOutVoltageBits); //2^bits
  int minVoltage = maximumOutVoltageInBits; //Set high value so it has to be adjusted. 
  analogWriteResolution(maximumOutVoltageBits);
  for(int i = 0; i<maximumOutVoltageInBits; i++){   //Check for every possible voltage level if it exceeds the minimum or maximum. 
    analogWrite(pwmPin, i);
    delay(1);
    voltage = analogRead(ADC);
    if (voltage>maxVoltage){
      maxVoltage = voltage;
    }
    else if(voltage<minVoltage){
      minVoltage = voltage;
    }
  }
  int meanVoltage = (maxVoltage - minVoltage)/2;
  returnVoltages[0] = maxVoltage;
  returnVoltages[1] = minVoltage;
  returnVoltages[2] = meanVoltage;
  return returnVoltages;
}

bool lambda_calibration_derivative(int meanVoltage){
  analogWrite(pwmPin, meanVoltage);
  delay(1);
  int voltageMeanRead = analogRead(ADC);
  int meanError = meanVoltage - voltageMeanRead;
  analogWrite(pwmPin, meanVoltage + 2);
  delay(1);
  int voltageMeanReadHigh = analogRead(ADC);
  int highMeanError = meanVoltage + 2 - voltageMeanReadHigh;
  //Check if derivative is positive or negative:
  int error = highMeanError - meanError;
  if(error<0){
    return false;
  }
  return true; 
  
}

void IRAM_ATTR Timer0_ISR() //Interrupt function when timer is at 1ms. In this timer the PID controller will function. 
{
  input_bits = analogRead(analogreadpin);    // Read input value in bits
  input = ((int)input_bits)*3.3/4095;
  output = pid.compute(input)*4095/3.3;
  output_bits = static_cast<uint16_t>(round(output));// Compute PID control signal
  analogWrite(PWMpin, output_bits);
}

void Task1code( void * pvParameters ){

  for(;;){
    if(Serial.available()){
      byte output = Serial.read();
      Serial2.write(output);
    }
  }
}


void setup() {
  // put your setup code here, to run once:
  
  //Set the PID controller setpoint in 12 bit.
  pid.setSetpoint(setPoint);

  //Set the PID controller maximum output as 3.3V
  pid.setMaxOutput(maxOutput);
  
  //Set the write resolution off the pwm signal to 12 bit(same as read default)
  analogWriteResolution(12);
  
  //open serial communications on baud rate 115200
  Serial.begin(115200);
  Serial2.begin(115200);
  
  //Perform a check with the pc if they can send and receive
  startupCheck();

  //config task to a core. 
  xTaskCreatePinnedToCore(
                    Task1code,   /* Task function. */
                    "Task1",     /* name of task. */
                    10000,       /* Stack size of task */
                    NULL,        /* parameter of the task */
                    1,           /* priority of the task */
                    &Task1,      /* Task handle to keep track of created task */
                    1);          /* pin task to core 1 */ 
                    
  //Interrupt timer for every 1ms. 
  Timer0_Cfg = timerBegin(0, 80, true); //80Mhz/80 = 1 Mhz
  timerAttachInterrupt(Timer0_Cfg, &Timer0_ISR, true);
  timerAlarmWrite(Timer0_Cfg, 1000, true); //Count till 1000 = 1Khz
  timerAlarmEnable(Timer0_Cfg);
}

void loop() {
  // put your main code here, to run repeatedly:

}
