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
}

void PIDController::setSetpoint(double sp) {
  setpoint = sp;
}

double PIDController::compute(double inputValue) {
  input = inputValue;

  // Calculate time difference
  unsigned long currentTime = millis();
  deltaTime = 1.0 / 1000.0;  // Convert milliseconds to seconds

  // Perform PID calculations
  double error = setpoint - input;
  integral += error * deltaTime;
  if integral>5000{
    integral = 5000;
  }
  else if (integral<-5000){
    integral = -5000;
  }
  double derivative = (input - prevInput) / deltaTime;
  output = Kp * error + Ki * integral + Kd * derivative;

  // Update variables for the next iteration
  prevInput = input;
  prevTime = currentTime;

  return output;
}
