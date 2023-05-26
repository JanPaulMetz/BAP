#define LED 2
#define baudrate 115200 //Baud rate FPGA = 115200
#define potPin 36 //Pin to measure voltage. 
#define LED 2
#define pwmPin 23
#define ADC 4
#include <PID_v1.h>

//Define Variables we'll be connecting to
double Setpoint, Input, Output;
float newError;
float minError = 256;

//Specify the links and initial tuning parameters
PID myPID(&Input, &Output, &Setpoint,2,5,1, DIRECT);
 
hw_timer_t *Timer0_Cfg = NULL;
 
void IRAM_ATTR Timer0_ISR() //Interrupt function when timer is at 1ms. 
{
    //Get the input voltage level
    Input = analogRead(ADC); //Divide by 2 to get 8 bits resolution.
    //Compute the PID
    myPID.Compute();
    //Write the output of the PID controller as a pwm voltage. 
    analogWrite(pwmPin, Output);
    //ledcWrite(pwmChannel, 127);
    
}

void setup()
{
    //pinMode(potPin,INPUT_PULLUP);
    pinMode(LED, OUTPUT);

    //initialize the variables we're linked to
    analogWriteResolution(12);
    Input = analogRead(ADC); 
    Setpoint = 2048;

    //turn the PID on
    myPID.SetSampleTime(1);
    myPID.SetMode(AUTOMATIC);
    //Interrupt timer for every 1ms. 
    Timer0_Cfg = timerBegin(0, 8000, true);
    timerAttachInterrupt(Timer0_Cfg, &Timer0_ISR, true);
    timerAlarmWrite(Timer0_Cfg, 10000, true);
    timerAlarmEnable(Timer0_Cfg);
    //Start serial communication on:
    Serial.begin(baudrate); //USB port 
    pinMode(LED, OUTPUT);
    digitalWrite(LED, HIGH);
    
}
void loop()
{
  //Print errors
    newError = abs(Input-Output);
    Serial.println("-----");
    Serial.println(millis());
    Serial.println(Input);
    Serial.println(Output);
    Serial.println(newError);
    delay(1);
}
