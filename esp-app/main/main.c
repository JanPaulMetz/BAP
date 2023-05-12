/* UART Echo Example

   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
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

const uart_port_t uart_num = UART_NUM_0;

static void init_led(void)
{
    gpio_set_direction(GPIO_NUM_2, GPIO_MODE_OUTPUT); //Set the pin direction of the led(pin2) to out. 
    gpio_set_level(GPIO_NUM_2, 0); //Put the blue LED(pin2) off. 
}

static void init_uart(void)
{
    
   
   // Setup UART buffered IO with event queue
    const int uart_buffer_size = (1024*2);
    QueueHandle_t uart_queue;
    // Install UART driver using an event queue here
    ESP_ERROR_CHECK(uart_driver_install(uart_num, uart_buffer_size, \
                                        uart_buffer_size, 10, &uart_queue, 0));
    
    // Configure UART parameters
    ESP_ERROR_CHECK(uart_set_baudrate(uart_num, 115200));
    ESP_ERROR_CHECK(uart_set_word_length(uart_num, UART_DATA_8_BITS));
    ESP_ERROR_CHECK(uart_set_parity(uart_num,UART_PARITY_DISABLE));
    ESP_ERROR_CHECK(uart_set_stop_bits(uart_num, UART_STOP_BITS_1));
    ESP_ERROR_CHECK(uart_set_hw_flow_ctrl(uart_num, UART_HW_FLOWCTRL_DISABLE,122));
    ESP_ERROR_CHECK(uart_set_mode(uart_num, UART_MODE_UART));

    ESP_ERROR_CHECK(uart_set_pin(UART_NUM_0, 1, 3, 18, 19));



    //Blink Led
    vTaskDelay(2000/portTICK_PERIOD_MS);
    gpio_set_level(GPIO_NUM_2, 0); //Put the blue LED off.
    //Configure UART parameters
    vTaskDelay(2000/portTICK_PERIOD_MS);
    gpio_set_level(GPIO_NUM_2, 0); //Put the blue LED off.

}


int app_main(void)
{
    //Initialize:
    init_led();
    init_uart();
    //char* message = "Nog geen echo";
    
    while (1)
    {
        //gpio_set_level(GPIO_NUM_2, 0); //Put the blue LED off.
        vTaskDelay(500/portTICK_PERIOD_MS);
        
        // Read data from UART.
        uint8_t data[128];
        int length = 0;
        ESP_ERROR_CHECK(uart_get_buffered_data_len(uart_num, (size_t*)&length));
        length = uart_read_bytes(uart_num, data, length, 100);
        if(length>101){
            gpio_set_level(GPIO_NUM_2, 1); //Put the blue LED on.
        }
        //Write back data to UART.
        uart_write_bytes(uart_num, (const char*)data, length);
        vTaskDelay(500/portTICK_PERIOD_MS);
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
