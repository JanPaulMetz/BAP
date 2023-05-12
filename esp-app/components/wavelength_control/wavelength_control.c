#include <stdio.h>
#include "wavelength_control.h"

void init(){
    	
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
    // integral += (error*period); // Moet hier niet nog een tijd iets bij?
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
