#include "madfunctions.h"
#include "serialfunctions.h"

#define LED 2
#define PWMpin 25
#define analogreadpin 4
#define Size 10
#define resolution 8
#define percentToKeep 10

int lambda_calibration(){  //Function to calibrate the lambda control. 
  int delayTime = 1000;
  int voltage[Size];
  int timestamp[Size];
  int outliers[Size];
  int maxVoltage, minVoltage, meanVoltage;
  int count = 0;
  float madThreshold = 3.0;  // Threshold for outlier detection
  bool maxVoltageset = false, minVoltageset = false;

  // Calculate the number of values to keep
  int numToKeep = (Size * percentToKeep) / 100;

  //sweep voltage and measure the output back and put in array with its timestamps in another array. 
  //sweepMeasure(voltage, timestamp, delayTime, Size);
  //sineMeasure(voltage, timestamp, delayTime, Size);
  pulseMeasure(voltage,timestamp,delayTime,Size);

  //Cast int array to uint16_t array to be easier to send. 
  for (int i = 0; i < Size; i++) {
    outliers[i] = 0;
  }

  sendData(voltage,timestamp, Size);
  
  //Sort so the highest values are in the first places of the array. 
  insertionSortDesc(voltage, timestamp, Size);

  sendData(voltage,timestamp, numToKeep);

  // Calculate the median and MAD of the values to keep
  int median = calculateMedian(voltage, numToKeep);
  float mad = calculateMAD(voltage, numToKeep, median);

  sendConstant(median);

  // Print the cleaned array (remove outliers)
  for (int i = 0; i < numToKeep; i++) {
    int deviation = abs(voltage[i] - median);
    if (deviation / mad > madThreshold and !maxVoltageset) {
      outliers[i] = 1;
      //voltage[i] = median; //Set outliers to the median, so it can never be the extreme value.
      count++; //Set the index of the maximum number to a non outlier. 
    }
    else if (!maxVoltageset){
      maxVoltage = voltage[count];
      maxVoltageset = true;
    }
  }
  
  count = 0;

  insertionSortAsc(voltage, timestamp, outliers, Size);

  sendData(voltage,timestamp, numToKeep);

  // Calculate the median and MAD of the values to keep
  median = calculateMedian(voltage, numToKeep);
  mad = calculateMAD(voltage, numToKeep, median);

  sendConstant(median);

  // Print the cleaned array (remove outliers)
  for (int i = 0; i < numToKeep; i++) {
    int deviation = abs(voltage[i] - median);
    if (deviation / mad > madThreshold and !minVoltageset) {
      outliers[i] = 1;
      //voltage[i] = median; //Set outliers to the median, so it can never be the extreme value.
      count++; //Set the index of the maximum number to a non outlier. 
    }
    else if (!minVoltageset){
      minVoltage = voltage[count];
      minVoltageset = true;
    }
  }

  sendArray(outliers, Size); //Send array with indexes of outliers.
  sendData(voltage,timestamp, Size); //Send sorted array. 

  minVoltage = voltage[count];

  meanVoltage = (minVoltage + maxVoltage)/2;

  return meanVoltage;
  
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
  dacWrite(PWMpin, normalizeToBits(0.6));
  // put your setup code here, to run once:
  Serial.begin(115200);
  //Perform a check with the pc if they can send and receive
  startupCheck();

  int Meanvoltage = lambda_calibration(); 
  dacWrite(PWMpin, normalizeToBits(0.75));

}

void loop() {
  // put your main code here, to run repeatedly:

}

void sweepMeasure(int* voltage, int* timestamp, int delayTime, int sweepSize){
  int startTime = millis();
  for(int i = 0; i<sweepSize; i++){   //Check for every possible voltage level if it exceeds the minimum or maximum. 
    dacWrite(PWMpin, i);
    delay(delayTime);
    voltage[i] = analogRead(analogreadpin);
    timestamp[i] = millis()-startTime;
    
  }
}

void pulseMeasure(int* voltage, int* timestamp, int delayTime, int sweepSize){
  int startTime = millis();
  float minVoltage = 0.65;
  float maxVoltage = 0.75;
  float voltageToSend;
  for(int i = 0; i<sweepSize; i++){   //Check for every possible voltage level if it exceeds the minimum or maximum.
    voltageToSend = normalizeToBits(minVoltage) + normalizeToBits(maxVoltage - minVoltage)/sweepSize*i;
    dacWrite(PWMpin, int(voltageToSend));
    delay(delayTime);
    voltage[i] = analogRead(analogreadpin);
    timestamp[i] = millis()-startTime;
    
  }
}

void sineMeasure(int* voltage, int* timestamp, int delayTime, int sineSize){
  int startTime = millis();
  int amplitude = 64;
  int offset = 128;
  int writeValue;
  int noise_amplitude = 2;
  for (int i = 0; i < sineSize/180; i++){
    for (int deg = 0; deg < 360; deg = deg + 2) {
      // Calculate sine and write to DAC
      writeValue = int(offset + amplitude * sin(deg * PI / 180)) + random(-noise_amplitude, noise_amplitude);
//      if (deg == 90){
//        writeValue = writeValue + outlierAdd;
//      }
//      else if(deg == 270){
//        writeValue = writeValue - outlierAdd;
//      }
      dacWrite(PWMpin, writeValue);
      delay(delayTime);
      voltage[i*180+deg/2] = analogRead(analogreadpin);
      timestamp[i*180+deg/2] = millis()-startTime;
    }
  }
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

float normalizeToBits(float voltage){
  int bits;
  bits = voltage/3.3*255;
  return bits;
}

float normalizeToVoltage(int bits){
  int voltage;
  voltage = bits/255*3.3;
  return voltage;
}
