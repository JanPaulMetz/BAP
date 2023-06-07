#include <Arduino.h>

void sendData(int Data[], int Time[], int bits){
    //Variables used for sending to pc.
    uint16_t dataBits[bits];
    uint32_t timeBits[bits];

    uint8_t outputByteArray[2*bits]; //Voltage that have been measured out of the interferometer.
    uint8_t timeByteArray[4*bits];

    //Define variables for saving and sending. 
    uint8_t HighByte, MedHighByte, MedLowByte, LowByte;
    //Send to PC:
    for(int i = 0; i < bits; i++){
        dataBits[i] = static_cast<uint16_t>(Data[i]);
        timeBits[i] = static_cast<uint32_t>(Time[i]);
        //Put the voltage in 2 bytes and put it in the voltage array to send
        HighByte = (dataBits[i] >> 8) & 0xFF;
        LowByte = dataBits[i] & 0xFF;
        //Create data array with measured data to send via UART
        outputByteArray[2 * i] = HighByte;
        outputByteArray[1 + 2 * i] = LowByte;

        //Put the timestamp in 4 bytes and put it in the time array to send
        HighByte = (timeBits[i] >> 24) & 0xFF;
        MedHighByte = (timeBits[i] >> 16) & 0xFF;
        MedLowByte = (timeBits[i] >> 8) & 0xFF;
        LowByte = timeBits[i] & 0xFF;
        //Create timestamp array to send
        timeByteArray[4 * i] = HighByte;
        timeByteArray[1 + 4 * i] = MedHighByte;
        timeByteArray[2 + 4 * i] = MedLowByte;
        timeByteArray[3 + 4 * i] = LowByte;
    }
    Serial.write(outputByteArray, 2*bits);
    Serial.write(timeByteArray, 4* bits);

}

void sendConstant(int value){
    uint16_t bits;
    uint8_t output[2];
    uint8_t HighByte, LowByte;
    bits = static_cast<uint16_t>(value);
    HighByte = (bits >> 8) & 0xFF;
    LowByte = bits & 0xFF;
    output[0] = HighByte;
    output[1] = LowByte;
    Serial.write(output, 2);
}

void sendArray(int Data[], int bits){
    //Variables used for sending to pc.
    uint16_t dataBits[bits];

    uint8_t outputByteArray[2 * bits]; //Voltage that have been measured out of the interferometer.

    //Define variables for saving and sending. 
    uint8_t HighByte, LowByte;
    //Send to PC:
    for(int i = 0; i < bits; i++){
        dataBits[i] = static_cast<uint16_t>(Data[i]);
        //Put the voltage in 2 bytes and put it in the voltage array to send
        HighByte = (dataBits[i] >> 8) & 0xFF;
        LowByte = dataBits[i] & 0xFF;
        //Create data array with measured data to send via UART
        outputByteArray[2 * i] = HighByte;
        outputByteArray[1 + 2 * i] = LowByte;
    }
    Serial.write(outputByteArray, 2*bits);
}
