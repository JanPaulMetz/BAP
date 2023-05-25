#ifndef WAVELENGTH_CONTROL
#define WAVELENGTH_CONTROL

#include "esp_adc/adc_oneshot.h"
#include "esp_adc/adc_cali.h"

void adc_init(adc_oneshot_unit_handle_t adc_handle);
void adc_init_calibration(adc_cali_handle_t *adc_calibration_handle, bool *do_calibration);

void adc_single_read_print(adc_oneshot_unit_handle_t adc_handle, adc_cali_handle_t adc_calibration_handle, bool *do_calibration);

float calculate_dc_operating_point(adc_oneshot_unit_handle_t* adc_handle);
float update_control_signal(float setpoint, float interfero_dc, float period);

#endif


