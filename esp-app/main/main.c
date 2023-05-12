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

static void init_led(void)
{
    gpio_set_direction(GPIO_NUM_2, GPIO_MODE_OUTPUT); //Set the pin direction of the led(pin2) to out. 
    //gpio_set_level(GPIO_NUM_2, 1); //Put the blue LED(pin2) on. 
}

static void init_uart(void)
{
   const uart_port_t uart_num = UART_NUM_0;
    // uart_config_t uart_config = {
    //     .baud_rate = 115200,
    //     .data_bits = UART_DATA_8_BITS,
    //     .parity = UART_PARITY_DISABLE,
    //     .stop_bits = UART_STOP_BITS_1,
    //     .flow_ctrl = UART_HW_FLOWCTRL_CTS_RTS,
    //     .rx_flow_ctrl_thresh = 122
    // };
    // Configure UART parameters
    //ESP_ERROR_CHECK(uart_param_config(uart_num, &uart_config));
    ESP_ERROR_CHECK(uart_set_baudrate(uart_num, 115200));
    ESP_ERROR_CHECK(uart_set_word_length(uart_num, UART_DATA_8_BITS));
    ESP_ERROR_CHECK(uart_set_parity(uart_num,UART_PARITY_DISABLE));
    ESP_ERROR_CHECK(uart_set_stop_bits(uart_num, UART_STOP_BITS_1));
    ESP_ERROR_CHECK(uart_set_hw_flow_ctrl(uart_num, UART_HW_FLOWCTRL_CTS_RTS,122));
   // gpio_set_level(GPIO_NUM_2, 1); //Put the blue LED(pin2) on
    //ESP_ERROR_CHECK(uart_set_mode(uart_num, UART_MODE_UART));
    vTaskDelay(2000/portTICK_PERIOD_MS);

    gpio_set_level(GPIO_NUM_2, 0); //Put the blue LED off.
    //Configure UART parameters
    vTaskDelay(3000/portTICK_PERIOD_MS);
    gpio_set_level(GPIO_NUM_2, 1); //Put the blue LED off.

}


int app_main(void)
{
    //Initialize:
    init_led();
    init_uart();
    while(1){
         gpio_set_level(GPIO_NUM_2, 0); //Put the blue LED off.
        // break;
        vTaskDelay(1000/portTICK_PERIOD_MS);
        gpio_set_level(GPIO_NUM_2, 1); //Put the blue LED on.
        vTaskDelay(1000/portTICK_PERIOD_MS);
    }
   
    //init_uart();
    //Loop:
    // while(1)
    // {
    //     gpio_set_level(GPIO_NUM_2, 0); //Put the blue LED off.
    //     // break;
    //     vTaskDelay(1000/portTICK_PERIOD_MS);
    //     gpio_set_level(GPIO_NUM_2, 1); //Put the blue LED on.
    //     vTaskDelay(1000/portTICK_PERIOD_MS);
    //     // Write data to UART.
    //     // char* test_str = "H\n";
    //     // uart_write_bytes(UART_NUM_0, (const char*)test_str, strlen(test_str));
    //     // vTaskDelay(1000/portTICK_PERIOD_MS);
    //     // gpio_set_level(GPIO_NUM_2, 0);
    //     // vTaskDelay(1000/portTICK_PERIOD_MS);
    // }
    return 0;
}
