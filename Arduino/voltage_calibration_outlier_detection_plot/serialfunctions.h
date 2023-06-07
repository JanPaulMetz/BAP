#ifndef DATA_SEND_H
#define DATA_SEND_H

#include <Arduino.h>

const int CHUNK_SIZE = 64;  // Size of each chunk to send

void sendData(int Data[], int Time[], int bits);
void sendConstant(int value);
void sendArray(int Data[], int bits);

#endif
