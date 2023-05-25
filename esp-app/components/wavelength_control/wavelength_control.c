#include <stdio.h>
#include "wavelength_control.h"
#include "esp_adc/adc_oneshot.h"
#include "driver/gpio.h"
#include "esp_log.h"
#include "esp_adc/adc_cali.h"
#include "esp_adc/adc_cali_scheme.h"

const static char *TAG = "VOLTAGE READER";



bool example_adc_calibration_init(adc_unit_t unit, adc_atten_t atten, adc_cali_handle_t *out_handle);
void example_adc_calibration_deinit(adc_cali_handle_t handle);


// initialize adc unit. 
void adc_init(adc_oneshot_unit_handle_t adc_handle){
    //set configuration for the unit. 
    adc_oneshot_unit_init_cfg_t init_config1 = {
        .unit_id = ADC_UNIT_1, 
        .ulp_mode = ADC_ULP_MODE_DISABLE,
    };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&init_config1, &adc_handle)); //create new unit with configurations
    //set channel configurations. 
    adc_oneshot_chan_cfg_t config = {
    .bitwidth = ADC_BITWIDTH_DEFAULT, //Default bitwidth = 12
    .atten = ADC_ATTEN_DB_11,       //Set the range to measure. 
    };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc_handle, ADC_CHANNEL_0, &config)); //create 

    
}
// initialiaze the calibration. 
void adc_init_calibration(adc_cali_handle_t *adc_calibration_handle, bool *do_calibration){
    adc_calibration_handle = NULL;
    *do_calibration = example_adc_calibration_init(ADC_UNIT_1, ADC_ATTEN_DB_11, adc_calibration_handle);
}

void adc_single_read_print(adc_oneshot_unit_handle_t adc_handle, adc_cali_handle_t adc_calibration_handle, bool *do_calibration){
    int raw_output[1][10];
    int voltage[1][10];
    ESP_ERROR_CHECK(adc_oneshot_read(adc_handle,ADC_CHANNEL_0,*raw_output));
    ESP_LOGI(TAG, "ADC%d Channel[%d] Raw Data: %d", ADC_UNIT_1 + 1, ADC_CHANNEL_0, raw_output[0][0]);
    if (do_calibration) {
            ESP_ERROR_CHECK(adc_cali_raw_to_voltage(adc_calibration_handle, raw_output[0][0], &voltage[0][0]));
            ESP_LOGI(TAG, "ADC%d Channel[%d] Cali Voltage: %d mV", ADC_UNIT_1 + 1, ADC_CHANNEL_0, voltage[0][0]);
    }
}

float calculate_dc_operating_point(adc_oneshot_unit_handle_t* adc_handle){
    float minimum_dc = 0;
    float maximum_dc  = 0;
    float operating_point;
    //float voltage[1][10];
    int adc_raw[1][10];

    ESP_ERROR_CHECK(adc_oneshot_read(*adc_handle, ADC_CHANNEL_0, &adc_raw[0][0]));
    //voltage[0][0] = adc_raw[0][0] * 3 / 4096; 

    operating_point = (minimum_dc + maximum_dc)/2;

    return operating_point;
}

    

float update_control_signal(float setpoint, float interfero_dc, float period)
{
    // float error, p_term, i_term, control_signal, integral;

    // // Proportional and Integral gains:
    // const float k_p = 1.0;
    // const float k_i = 0.0;
    // const float maxintegral = 300;
    // const float minintegral = -300;

    // // Calculate error:
    // error = setpoint - interfero_dc;

    // //Calculate integral:
    // integral += (error); // Moet hier niet nog een tijd iets bij?
    // // Prevent winding due to integral term: 
    // if(integral>maxintegral){
    //     integral = maxintegral;
    // }
    // else if (integral<minintegral)
    // {
    //     integral = minintegral;
    // }

    // // Calculate PI terms:
    // p_term = k_p*error;
    // i_term = k_i*integral; 

    // // Calculate new control_signal:
    // control_signal = p_term + i_term;

    // return control_signal; 
    return 1;
}

/*---------------------------------------------------------------
        ADC Calibration
---------------------------------------------------------------*/
bool example_adc_calibration_init(adc_unit_t unit, adc_atten_t atten, adc_cali_handle_t *out_handle)
{
    adc_cali_handle_t handle = NULL;
    esp_err_t ret = ESP_FAIL;
    bool calibrated = false;

#if ADC_CALI_SCHEME_CURVE_FITTING_SUPPORTED
    if (!calibrated) {
        ESP_LOGI(TAG, "calibration scheme version is %s", "Curve Fitting");
        adc_cali_curve_fitting_config_t cali_config = {
            .unit_id = unit,
            .atten = atten,
            .bitwidth = ADC_BITWIDTH_DEFAULT,
        };
        ret = adc_cali_create_scheme_curve_fitting(&cali_config, &handle);
        if (ret == ESP_OK) {
            calibrated = true;
        }
    }
#endif

#if ADC_CALI_SCHEME_LINE_FITTING_SUPPORTED
    if (!calibrated) {
        ESP_LOGI(TAG, "calibration scheme version is %s", "Line Fitting");
        adc_cali_line_fitting_config_t cali_config = {
            .unit_id = unit,
            .atten = atten,
            .bitwidth = ADC_BITWIDTH_DEFAULT,
        };
        ret = adc_cali_create_scheme_line_fitting(&cali_config, &handle);
        if (ret == ESP_OK) {
            calibrated = true;
        }
    }
#endif

    *out_handle = handle;
    if (ret == ESP_OK) {
        ESP_LOGI(TAG, "Calibration Success");
    } else if (ret == ESP_ERR_NOT_SUPPORTED || !calibrated) {
        ESP_LOGW(TAG, "eFuse not burnt, skip software calibration");
    } else {
        ESP_LOGE(TAG, "Invalid arg or no memory");
    }

    return calibrated;
}

void example_adc_calibration_deinit(adc_cali_handle_t handle)
{
#if ADC_CALI_SCHEME_CURVE_FITTING_SUPPORTED
    ESP_LOGI(TAG, "deregister %s calibration scheme", "Curve Fitting");
    ESP_ERROR_CHECK(adc_cali_delete_scheme_curve_fitting(handle));

#elif ADC_CALI_SCHEME_LINE_FITTING_SUPPORTED
    ESP_LOGI(TAG, "deregister %s calibration scheme", "Line Fitting");
    ESP_ERROR_CHECK(adc_cali_delete_scheme_line_fitting(handle));
#endif
}
