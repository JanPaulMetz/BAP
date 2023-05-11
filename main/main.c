/* 
    Main routine
*/
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "esp_log.h"
#include "wavelength_control.h"
#include "sdkconfig.h"

// #define TEST CONFIG_SOC_GPIO_SUPPORT_SLP_SWITCH
static const char *TAG = "example";

/* Use project configuration menu (idf.py menuconfig) to choose the GPIO to blink,
   or you can edit the following line and set a number here.
*/

void app_main(void)
{

    while (1) {
        test_serial();
        vTaskDelay(1);
    }
}
