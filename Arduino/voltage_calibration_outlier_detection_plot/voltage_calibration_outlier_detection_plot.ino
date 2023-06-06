#define LED 2
#define PWMpin 25
#define analogreadpin 4
#define Size 256 
#define resolution 8
#define percentToKeep 20

int lambda_calibration(){  //Function to calibrate the lambda control. 
  int delayTime = 1;
  int voltage[Size];
  int timestamp[Size];
  int outliers[Size];
  int maxVoltage, minVoltage, meanVoltage;
  int count = 0;
  float madThreshold = 1.0;  // Threshold for outlier detection
  bool maxVoltageset = false, minVoltageset = false;

  // Calculate the number of values to keep
  int numToKeep = (Size * percentToKeep) / 100;



  //sweep voltage and measure the output back and put in array with its timestamps in another array. 
  sweepMeasure(voltage, timestamp, delayTime);

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
    if (deviation / mad > madThreshold) {
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
    if (deviation / mad > madThreshold) {
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
  // put your setup code here, to run once:
  Serial.begin(115200);

  //Perform a check with the pc if they can send and receive
  startupCheck();

  int Meanvoltage = lambda_calibration(); 

}

void loop() {
  // put your main code here, to run repeatedly:

}

void sweepMeasure(int* voltage, int* timestamp, int delayTime){
  int startTime = millis();
  for(int i = 0; i<Size; i++){   //Check for every possible voltage level if it exceeds the minimum or maximum. 
    dacWrite(PWMpin, i);
    delay(delayTime);
    voltage[i] = analogRead(analogreadpin);
    timestamp[i] = millis()-startTime;
    
  }
}

// Insertion Sort algorithm (descending order, without timestamps)
void insertionSort(int arr[], int length) {
  for (int i = 1; i < length; i++) {
    int key = arr[i];
    int j = i - 1;
    while (j >= 0 && arr[j] < key) {
      arr[j + 1] = arr[j];
      j = j - 1;
    }
    arr[j + 1] = key;
  }
}

// Insertion Sort algorithm (descending order)
void insertionSortDesc(int arr[], int timearr[], int length) {
  for (int i = 1; i < length; i++) {
    int key = arr[i];
    int timeKey = timearr[i];
    int j = i - 1;
    while (j >= 0 && arr[j] < key) {
      arr[j + 1] = arr[j];
      timearr[j + 1] = timearr[j];
      j = j - 1;
    }
    arr[j + 1] = key;
    timearr[j + 1] = timeKey;
  }
}

// Insertion Sort algorithm (ascending order)
void insertionSortAsc(int arr[], int timearr[],int outlierarr[], int length) {
  for (int i = 1; i < length; i++) {
    int key = arr[i];
    int timeKey = timearr[i];
    int outlierKey = outlierarr[i];
    int j = i - 1;
    while (j >= 0 && arr[j] > key) {
      arr[j + 1] = arr[j];
      timearr[j + 1] = timearr[j];
      outlierarr[j + 1] = outlierarr[j];
      j = j - 1;
    }
    arr[j + 1] = key;
    timearr[j + 1] = timeKey;
    outlierarr[j + 1] = outlierKey;
  }
}


// Calculate the median of the array values
int calculateMedian(int arr[], int length) {
  if (length % 2 == 0) {
    return (arr[length / 2 - 1] + arr[length / 2]) / 2;
  }
  else {
    return arr[length / 2];
  }
}

// Calculate the Median Absolute Deviation (MAD) of the array values
float calculateMAD(int arr[], int length, int median) {
  int deviations[length];
  for (int i = 0; i < length; i++) {
    deviations[i] = abs(arr[i] - median);
  }

  insertionSort(deviations, length);

  if (length % 2 == 0) {
    return (deviations[length / 2 - 1] + deviations[length / 2]) / 2.0;
  }
  else {
    return deviations[length / 2];
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

void sendData(int Data[],int Time[],int bits){
    //Variables used for sending to pc.
    uint16_t dataBits[bits];
    uint32_t timeBits[bits];

    byte outputByteArray[2*bits]; //Voltage that have been measured out of the interferometer.
    byte timeByteArray[4*bits];

    //Define variables for savind and sending. 
    byte HighByte, MedHighByte, MedLowByte, LowByte;
    //Send to PC:
    for(int i = 0; i < bits; i++){
      dataBits[i] = static_cast<uint16_t>(Data[i]);
      timeBits[i] = static_cast<uint32_t>(Time[i]);
      //Put the voltage in 2 bytes and put it in the voltage array to send
      HighByte = (dataBits[i]>>8) & 0xFF;
      LowByte = dataBits[i] & 0xFF;
      //Create data array with measured data to send via uart
      outputByteArray[2*i] = HighByte;
      outputByteArray[1+2*i] = LowByte;
      
      //Put the timestamp in 4 bytes and put in the time array to send
      HighByte = (timeBits[i]>>24) & 0xFF;
      MedHighByte = (timeBits[i]>>16) & 0xFF;
      MedLowByte = (timeBits[i]>>8) & 0xFF;
      LowByte = timeBits[i] & 0xFF;
      //Create timestamp array to send
      timeByteArray[4*i] = HighByte;
      timeByteArray[1+4*i] = MedHighByte;
      timeByteArray[2+4*i] = MedLowByte;
      timeByteArray[3+4*i] = LowByte;
    }
    Serial.write(outputByteArray,2*bits);
    Serial.write(timeByteArray,4*bits);
  }

void sendConstant(int value){
  uint16_t bits;
  byte output[2];
  byte HighByte, LowByte;
  bits = static_cast<uint16_t>(value);
  HighByte = (bits>>8) & 0xFF;
  LowByte = bits & 0xFF;
  output[0] = HighByte;
  output[1] = LowByte;
  Serial.write(output,2);
}

void sendArray(int Data[],int bits){
    //Variables used for sending to pc.
    uint16_t dataBits[bits];

    byte outputByteArray[2*bits]; //Voltage that have been measured out of the interferometer.

    //Define variables for savind and sending. 
    byte HighByte, LowByte;
    //Send to PC:
    for(int i = 0; i < bits; i++){
      dataBits[i] = static_cast<uint16_t>(Data[i]);
      //Put the voltage in 2 bytes and put it in the voltage array to send
      HighByte = (dataBits[i]>>8) & 0xFF;
      LowByte = dataBits[i] & 0xFF;
      //Create data array with measured data to send via uart
      outputByteArray[2*i] = HighByte;
      outputByteArray[1+2*i] = LowByte;
    }
    Serial.write(outputByteArray,2*bits);
  }
