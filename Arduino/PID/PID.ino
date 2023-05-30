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

float Kp = 2;//-0.0127;
float Ki = 5;//-0.00965;
float Kd = 1;//-0.0000487;
int PIDSetPoint = 1024;


//Specify the links and initial tuning parameters
PID myPID(&Input, &Output, &Setpoint,0,0,0, DIRECT);//Tunings first set to some random variables, will later be changed due to direction.

void setup()
{  
  //initialize the variables we're linked to
  analogWriteResolution(12);
  Input = analogRead(ADC); 
  Setpoint = PIDSetPoint;

  //turn the PID on
  myPID.SetSampleTime(1);
  myPID.SetOutputLimits(0,4095);
  myPID.SetMode(AUTOMATIC);
  //Retune PID:
  if((Kp < 0)&&((Ki < 0)&&(Kd < 0))){
    Kp = -Kp;
    Ki = -Ki;
    Kd = -Kd;
    myPID.SetTunings(Kp,Ki,Kd);
    myPID.SetControllerDirection(REVERSE);
  }
  else if((Kp > 0)&&((Ki > 0)&&(Kd > 0))){
    myPID.SetTunings(Kp,Ki,Kd);
    myPID.SetControllerDirection(DIRECT);
  }
  
  
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
    analogWrite(pwmPin, Output);
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
