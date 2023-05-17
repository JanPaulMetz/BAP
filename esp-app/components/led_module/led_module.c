#include <stdio.h>
#include "driver/gpio.h"
#include "led_module.h"


void init_led(void)
{
    gpio_set_direction(GPIO_NUM_2, GPIO_MODE_OUTPUT); //Set the pin direction of the led(pin2) to out. 
    gpio_set_level(GPIO_NUM_2, 0); //Put the blue LED(pin2) off. 
}
