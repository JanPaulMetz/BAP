#ifndef PIDCONTROLLER_H
#define PIDCONTROLLER_H

class PIDController {
  private:
    double Kp;              // Proportional gain
    double Ki;              // Integral gain
    double Kd;              // Derivative gain
    double setpoint;        // Desired setpoint
    double input;           // Current input value
    double output;          // Output value from the controller
    double prevInput;       // Previous input value
    double integral;        // Integral term
    unsigned long prevTime; // Previous time
    double deltaTime;       // Time difference
    double capSize;         // Integral capsize

  public:
    PIDController(double kp, double ki, double kd);
    void setSetpoint(double sp);
    double compute(double inputValue);
};

#endif
