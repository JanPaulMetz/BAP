#include <Arduino.h>

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
