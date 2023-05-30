#include "pidclass.h"

#define pwmPin 23
#define ADC 4

double Kp = 2;//-0.0127;
double Ki = 5;//-0.00965;
double Kd = 1;//-0.0000487;
double input;
double output;

PIDController pid(Kp, Ki, Kd);  // Create a PID controller object with specified gains

hw_timer_t *Timer0_Cfg = NULL;
 
void IRAM_ATTR Timer0_ISR() //Interrupt function when timer is at 1ms. 
{
  input = readInput();                // Read input value (e.g., sensor reading)
  output = pid.compute(input);        // Compute PID control signal
  setOutput(output); 
}

void setup() {
  // Set up your hardware and initial configurations here
  pid.setSetpoint(2047);
  analogWriteResolution(12);
  Serial.begin(115200);
  //Interrupt timer for every 1ms. 
  Timer0_Cfg = timerBegin(0, 80, true); //1Mhz
  timerAttachInterrupt(Timer0_Cfg, &Timer0_ISR, true);
  timerAlarmWrite(Timer0_Cfg, 1000, true); //counts to 1000 -> 1Khz = 1ms
  timerAlarmEnable(Timer0_Cfg);
}

void loop() {
                          // Set the output value based on the control signal
  Serial.print("input: ");
  Serial.print(input);
  Serial.println();
  Serial.print("output: ");
  Serial.print(output);
  Serial.println();
  // Add a delay if necessary
  delay(1);  // Adjust the delay time as per your application requirements
}

double readInput() {
  return analogRead(ADC);  // Assuming a 3.3V reference and a 12-bit ADC
}

void setOutput(double output) {
  analogWrite(pwmPin, output);  
}
