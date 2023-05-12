/* UART Echo Example

   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
*/
#include <stdio.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include "string.h"
#include "driver/uart.h"
#include "driver/gpio.h"
#include "wavelength_control.h"

void init(void)
{
    gpio_set_direction(GPIO_NUM_2, GPIO_MODE_OUTPUT); //Set the pin direction of the led to out. 
    gpio_set_level(GPIO_NUM_2, 1); //Put the blue LED on. 
}



void app_main(void)
{
    /* Configure parameters of an UART driver,
     * communication pins and install the driver */


    // uart_config_t uart_config = {
    //     .baud_rate = 115200,
    //     .data_bits = UART_DATA_8_BITS,
    //     .parity = UART_PARITY_DISABLE,
    //     .stop_bits = UART_STOP_BITS_1,
    //     .flow_ctrl = UART_HW_FLOWCTRL_CTS_RTS,
    //     .rx_flow_ctrl_thresh = 122,
    // };
    // Configure UART parameters
    // ESP_ERROR_CHECK(uart_param_config(UART_NUM_0, &uart_config));

    // init pin 2 
    
    init();
    while(1)
    {
        gpio_set_level(GPIO_NUM_2, 0); //Put the blue LED on.
        // break;
        vTaskDelay(1000/portTICK_PERIOD_MS);
        gpio_set_level(GPIO_NUM_2, 1); //Put the blue LED on.
        vTaskDelay(1000/portTICK_PERIOD_MS);
        // Write data to UART.
        // char* test_str = "H\n";
        // uart_write_bytes(UART_NUM_0, (const char*)test_str, strlen(test_str));
        // vTaskDelay(1000/portTICK_PERIOD_MS);
        // gpio_set_level(GPIO_NUM_2, 0);
        // vTaskDelay(1000/portTICK_PERIOD_MS);
    }
}
