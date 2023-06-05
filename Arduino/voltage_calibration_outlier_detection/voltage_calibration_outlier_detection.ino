#define PWMpin 25
#define analogreadpin 4
#define Size 256 //12 bit resolution
#define resolution 8
#define percentToKeep 10

int lambda_calibration(){  //Function to calibrate the lambda control. 
  int delayTime = 1;
  int voltage[Size];
  int timestamp[Size];
  int maxVoltage, minVoltage, meanVoltage;
  int count = 0;
  float madThreshold = 5.0;  // Threshold for outlier detection

  //sweep voltage and measure the output back and put in array with its timestamps in another array. 
  sweepMeasure(voltage, timestamp, delayTime);

  //Sort so the highest values are in the first places of the array. 
  insertionSortDesc(voltage, timestamp, Size);

  // Calculate the number of values to keep
  int numToKeep = (Size * percentToKeep) / 100;

  // Calculate the median and MAD of the values to keep
  int median = calculateMedian(voltage, numToKeep);
  float mad = calculateMAD(voltage, numToKeep, median);

  // Print the cleaned array (remove outliers)
  for (int i = 0; i < numToKeep; i++) {
    int deviation = abs(voltage[i] - median);
    if (deviation / mad > madThreshold) {
      Serial.print("OUTLIER!: ");
      Serial.println(voltage[i]);
      voltage[i] = median; //Set outliers to the median, so it can never be the extreme value.
      count++; //Set the index of the maximum number to a non outlier. 
    }
  }
  
  maxVoltage = voltage[count];
  count = 0;

  insertionSortAsc(voltage, timestamp, Size);

  // Calculate the median and MAD of the values to keep
  median = calculateMedian(voltage, numToKeep);
  mad = calculateMAD(voltage, numToKeep, median);

  // Print the cleaned array (remove outliers)
  for (int i = 0; i < numToKeep; i++) {
    int deviation = abs(voltage[i] - median);
    if (deviation / mad > madThreshold) {
      Serial.print("OUTLIER!: ");
      Serial.println(voltage[i]);
      voltage[i] = median; //Set outliers to the median, so it can never be the extreme value.
      count++; //Set the index of the maximum number to a non outlier. 
    }
  }

  minVoltage = voltage[count];
  Serial.print("minimum voltage: ");
  Serial.println(minVoltage);

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

  int Meanvoltage = lambda_calibration();
  Serial.print("Mean voltage : ");
  Serial.println(Meanvoltage);
  

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
void insertionSortAsc(int arr[], int timearr[], int length) {
  for (int i = 1; i < length; i++) {
    int key = arr[i];
    int timeKey = timearr[i];
    int j = i - 1;
    while (j >= 0 && arr[j] > key) {
      arr[j + 1] = arr[j];
      timearr[j + 1] = timearr[j];
      j = j - 1;
    }
    arr[j + 1] = key;
    timearr[j + 1] = timeKey;
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
