#define LED 2
#define baudrate 115200 //Baud rate FPGA = 115200
#define potPin 36 //Pin to measure voltage. 

int potValue = 0;
int message;
 
hw_timer_t *Timer0_Cfg = NULL;

int timerCore;
 
void IRAM_ATTR Timer0_ISR() //Interrupt function when timer is at 1ms. 
{
//    digitalWrite(LED, !digitalRead(LED));
    
}

void startup_check(){
    while (1)
    {
        //Delay to make sure serial does not overflow fast. 
        delay(100);
        // Read data from UART.
        int inByte = Serial.read();
        int outByte;
        
        if(inByte == 0x41){
            digitalWrite(LED, HIGH); //Put the blue LED(pin2) on
            outByte = 0x42;              //Send back confirmation for the start message. 
            Serial.write(outByte); //Send five times to make sure it reaches the pc. 
            break;
        }
    }
    delay(500);
    digitalWrite(LED, LOW);
}

void setup()
{
    pinMode(potPin,INPUT_PULLUP);
    pinMode(LED, OUTPUT);
    //Interrupt timer for every 1ms. 
    Timer0_Cfg = timerBegin(0, 8000, true);
    timerAttachInterrupt(Timer0_Cfg, &Timer0_ISR, true);
    timerAlarmWrite(Timer0_Cfg, 10000, true);
    timerAlarmEnable(Timer0_Cfg);
    //Start serial communication on:
    Serial.begin(115200); //USB port 
    Serial2.begin(115200); //Uart Pins Uart2_tx & Uart2_rx.
    startup_check();
    
}
void loop()
{
  //Serial2.write(101);
  //potValue = analogRead(potPin);
  //Serial.println(potValue);
  delay(250);
  digitalWrite(LED, HIGH);
 // message = Serial.read();
  //delay(0.1);
  //Serial.write(message);
  delay(250);
  digitalWrite(LED, LOW);
  
  
    // Do Nothing!
}
