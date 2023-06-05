#define PWMpin 23
#define analogreadpin 4

int* lambda_calibration(int maximumOutVoltageBits){  //Function to calibrate the lambda control. 
  int* returnVoltages = new int[3];
  int voltage, maxVoltage = 0; //Set lowest value possible so it always goes up. 
  int maximumOutVoltageInBits = pow(2, maximumOutVoltageBits); //2^bits
  int minVoltage = maximumOutVoltageInBits; //Set high value so it has to be adjusted. 
  analogWriteResolution(maximumOutVoltageBits);
  for(int i = 0; i<maximumOutVoltageInBits; i++){   //Check for every possible voltage level if it exceeds the minimum or maximum. 
    analogWrite(PWMpin, i);
    delay(1);
    voltage = analogRead(analogreadpin);
    if (voltage > maxVoltage){
      maxVoltage = voltage;
    }
    else if(voltage < minVoltage){
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
  analogWrite(PWMpin, meanVoltage);
  delay(1);
  int voltageMeanRead = analogRead(analogreadpin);
  int meanError = meanVoltage - voltageMeanRead;
  analogWrite(PWMpin, meanVoltage + 2);
  delay(1);
  int voltageMeanReadHigh = analogRead(analogreadpin);
  int highMeanError = meanVoltage + 2 - voltageMeanReadHigh;
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
