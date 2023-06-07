#ifndef MADFUNCTIONS_H
#define MADFUNCTIONS_H

#include <Arduino.h>


void insertionSort(int arr[], int length);
void insertionSortDesc(int arr[], int timearr[], int length);
void insertionSortAsc(int arr[], int timearr[], int outlierarr[], int length);
int calculateMedian(int arr[], int length);
float calculateMAD(int arr[], int length, int median);

#endif
