/*********
  Rui Santos
  Complete project details at http://randomnerdtutorials.com  
*********/

TaskHandle_t Task1;

// LED pins
const int led1 = 2;
const int led2 = 4;

hw_timer_t *Timer0_Cfg = NULL;

int timerCore;
 
void IRAM_ATTR Timer0_ISR() //Interrupt function when timer is at 1ms. 
{
  timerCore = xPortGetCoreID();
  digitalWrite(led1, !digitalRead(led1));
}

void setup() {
  Serial.begin(115200); 
  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);

  //create a task that will be executed in the Task1code() function, with priority 1 and executed on core 0
  xTaskCreatePinnedToCore(
                    Task1code,   /* Task function. */
                    "Task1",     /* name of task. */
                    10000,       /* Stack size of task */
                    NULL,        /* parameter of the task */
                    1,           /* priority of the task */
                    &Task1,      /* Task handle to keep track of created task */
                    1);          /* pin task to core 1 */                  
  delay(500); 

  //Interrupt timer for every 1ms. 
  Timer0_Cfg = timerBegin(0, 80, true); //80Mhz/80 = 1 Mhz
  timerAttachInterrupt(Timer0_Cfg, &Timer0_ISR, true);
  timerAlarmWrite(Timer0_Cfg, 1000000, true); //Count till 1000 = 1Khz
  timerAlarmEnable(Timer0_Cfg);
}

//Task1code: blinks an LED every 1000 ms
void Task1code( void * pvParameters ){
  Serial.print("Task1 running on core ");
  Serial.println(xPortGetCoreID());
  Serial.print("Timer running on core ");
  Serial.println(timerCore);

  for(;;){
    
  } 
}

void loop() {
  
}
