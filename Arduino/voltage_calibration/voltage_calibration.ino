#define pwmPin 23
#define ADC 4

int lambda_calibration(int maximumOutVoltageBits){  //Function to calibrate the lambda control. 
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
  return maxVoltage, minVoltage, meanVoltage;
}

bool lambda_calibration_derivative(meanVoltage){
  analogWrite(pwmPin, meanVoltage);
  delay(1);
  voltageMeanRead = analogRead(ADC);
  int meanError = meanVoltage - voltageMeanRead;
  analogWrite(pwmPin, meanVoltage + 2);
  delay(1);
  voltageMeanReadHigh = analogRead(ADC);
  int highMeanError = meanvoltage + 2 - voltageMeanReadHigh;
  //Check if derivative is positive or negative:
  int error = highMeanError - meanError;
  if(error<0){
    return false;
  }
  return true; 
  
}

void setup() {
  // put your setup code here, to run once:

  

}

void loop() {
  // put your main code here, to run repeatedly:

}
