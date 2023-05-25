/********************************************************
 * PID Basic Example
 * Reading analog input 0 to control analog PWM output 3
 ********************************************************/

#include <PID_v1.h>

//Define Variables we'll be connecting to
double Setpoint, Input, Output;
float error;

//Specify the links and initial tuning parameters
PID myPID(&Input, &Output, &Setpoint,2,5,1, DIRECT);

void setup()
{
  //initialize the variables we're linked to
  Input = analogRead(39);
  Setpoint = 2000;

  //turn the PID on
  //myPID.SetSampleTime(1000);
  myPID.SetMode(AUTOMATIC);
  
  Serial.begin(115200);
}

void loop()
{
  Input = analogRead(39);
  delay(10);
  myPID.Compute();
  analogWrite(27,Output);
  error = Input-Output;
  Serial.println(error);
}
