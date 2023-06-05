const int arraySize = 100;  // Size of the array
const int percentToKeep = 20;  // Percentage of values to keep (highest)

int dataArray[arraySize];  // Array to store the data samples
float madThreshold = 2.0;  // Threshold for outlier detection (adjust as needed)

void setup() {
  Serial.begin(115200);

  // Prefill the dataArray with random samples
  randomSeed(analogRead(4));
  for (int i = 0; i < arraySize; i++) {
    dataArray[i] = random(0, 100);
  }

  // Sort the array in descending order
  insertionSort(dataArray, arraySize);

  // Calculate the number of values to keep
  int numToKeep = (arraySize * percentToKeep) / 100;

  // Calculate the median and MAD of the values to keep
  int median = calculateMedian(dataArray, numToKeep);
  float mad = calculateMAD(dataArray, numToKeep, median);

  // Print the cleaned array (remove outliers)
  for (int i = 0; i < numToKeep; i++) {
    int deviation = abs(dataArray[i] - median);
    if (deviation / mad <= madThreshold) {
      Serial.print(i);
      Serial.print(": ");
      Serial.println(dataArray[i]);
    }
    else{
      Serial.print(i);
      Serial.print(" OUTLIER! : ");
      Serial.println(dataArray[i]);
    }
  }
}

void loop() {
  // Main loop
}

// Insertion Sort algorithm (descending order)
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
