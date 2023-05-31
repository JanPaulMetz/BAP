#include "pidclass.h"
#include <Arduino.h>

PIDController::PIDController(double kp, double ki, double kd) {
  Kp = kp;
  Ki = ki;
  Kd = kd;
  setpoint = 0.0;
  input = 0.0;
  output = 0.0;
  prevInput = 0.0;
  integral = 0.0;
  prevTime = 0;
  deltaTime = 0.0;
  capSize = 5000;
}

void PIDController::setSetpoint(double sp) {
  setpoint = sp;
}

double PIDController::compute(double inputValue) {
  input = inputValue;

  // Calculate time difference
  unsigned long currentTime = millis();
  deltaTime = currentTime - prevTime; 

  // Perform PID calculations
  double error = setpoint - input;
  integral += error * deltaTime;
  
  // Cap the size of the integral to prevent other parameters from being to small. 
  if integral>capSize{
    integral = capSize;
  }
  else if (integral<-capSize){
    integral = -capSize;
  }

  //Calculate derivative part:
  double derivative = (input - prevInput) / deltaTime;
  
  //Calculate total output of the system
  output = Kp * error + Ki * integral + Kd * derivative;

  // Update variables for the next iteration
  prevInput = input;
  prevTime = currentTime;

  return output;
}
