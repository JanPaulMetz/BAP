/********************************************************
 * PID Basic Example
 * Reading analog input 0 to control analog PWM output 3
 ********************************************************/
#define LED 2
#define pwmPin 23
#define ADC 4
#include <PID_v1.h>

//Define Variables we'll be connecting to
double Setpoint, Input, Output;
float newError;
float minError = 256;

int pwmChannel = 0;
int frequence = 100000;
int resolution = 12;

//Specify the links and initial tuning parameters
PID myPID(&Input, &Output, &Setpoint,2,5,1, DIRECT);

void setup()
{  
  //initialize the variables we're linked to
  analogWriteResolution(12);
  Input = analogRead(ADC); 
  Setpoint = 127;

  //turn the PID on
  //myPID.SetSampleTime(1000);
  myPID.SetMode(AUTOMATIC);
  
  Serial.begin(115200);
  pinMode(LED, OUTPUT);
  digitalWrite(LED, HIGH);
}

void loop()
{
    //Get the input voltage level
    Input = analogRead(ADC); //Divide by 2 to get 8 bits resolution.
    //Compute the PID
    myPID.Compute();
    //Write the output of the PID controller as a pwm voltage. 
    analogWrite(pwmPin, 512);
    //ledcWrite(pwmChannel, 127);
    

    //Print errors
    newError = abs(Input-Output);
    Serial.println("-----");
    Serial.println(Input);
    Serial.println(Output);
    Serial.println(newError);
//    if(newError<minError){
//      minError = newError;
//      Serial.println(minError);
//    }
    delay(10);
}
