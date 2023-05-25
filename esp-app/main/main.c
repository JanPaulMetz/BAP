/* UART Echo Example

   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
*/

/*
GPIO PINOUT:
GPIO 1: UART 0 TX
GPIO 3: UART 0 RX
*/
#include <stdio.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include "esp_log.h"
#include "string.h"
#include "driver/uart.h"
#include "driver/gpio.h"
#include "wavelength_control.h"
#include "sdkconfig.h"
#include "led_module.h"
#include "uart_module.h"
#include "wavelength_control.h"


const uart_port_t uart_num = UART_NUM_0;

adc_oneshot_unit_handle_t adc_handle;
adc_cali_handle_t adc_calibration_handle;
bool do_calibration = NULL;



void startup_check(){
    while (1)
    {
        //Delay to make sure serial does not overflow fast. 
        vTaskDelay(100/portTICK_PERIOD_MS);
        // Read data from UART.
        uint8_t *data = (uint8_t *) malloc(128);
        uint8_t *send_data = (uint8_t *) malloc(2);
        int length = 0;
        ESP_ERROR_CHECK(uart_get_buffered_data_len(uart_num, (size_t*)&length));
        length = uart_read_bytes(uart_num, data, length, 100);
        
        if(*data == 0x41){
            gpio_set_level(GPIO_NUM_2, 1); //Put the blue LED(pin2) on
            *send_data = 0x42;              //Send back confirmation for the start message. 
            uart_write_bytes(uart_num,send_data,2);
            break;
        }
    }
}

// void get_frequency(){
//     bool freq_available;
//     float frequency;

//     return freq_available, frequency;
// }

void app_main(void)
{
    //Initialize:
    init_led();
    adc_init(adc_handle);
    while(1){
        adc_single_read_print(adc_handle, adc_calibration_handle, &do_calibration);
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
    // init_uart(UART_NUM_0);
    //Check if the connection over the serial port is established. 
    // startup_check();
    //Check if there is a frequency to work with:
    // while (x == True){
    //     x,y = get_frequency()
    //     )
    // }
    //Standard loop:
    // while (1){
    //     //Evaluate wavelength control
    //     //Operating point compensation
    //     //Instruction of pc?
    //     //If Yes->Execute instruction
    // }

    
}
