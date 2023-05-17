#include <stdio.h>
#include "uart_module.h"
#include "driver/uart.h"

void init_uart(uart_port_t uart_num)
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

    ESP_ERROR_CHECK(uart_set_pin(uart_num, 1, 3, 18, 19));

}
