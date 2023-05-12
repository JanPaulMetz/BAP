#include <stdio.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include "string.h"
#include "driver/uart.h"
#include "driver/gpio.h"
#include "wavelength_control.h"


void app_main(void)
{

    uart_config_t uart_config = {
        .baud_rate = 115200,
        .data_bits = UART_DATA_8_BITS,
        .parity = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_CTS_RTS,
        .rx_flow_ctrl_thresh = 122,
    };
    // Configure UART parameters
    ESP_ERROR_CHECK(uart_param_config(UART_NUM_0, &uart_config));

    while(1)
    {
        // Write data to UART.
        char* test_str = "H\n";
        uart_write_bytes(UART_NUM_0, (const char*)test_str, strlen(test_str));
        vTaskDelay(1000/portTICK_PERIOD_MS);
    }
}