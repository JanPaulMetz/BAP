int analogPin = 4; // potentiometer wiper (middle terminal) connected to analog pin A0
                    // outside leads to ground and +5V
uint16_t val;        // variable to store the value read

byte HighByte;
byte LowByte;

void setup() {
  Serial.begin(115200); // setup serial
}

void loop() {
  val = analogRead(analogPin); // read the input pin
  HighByte = (val>>8) & 0xFF;
  LowByte = val & 0xFF;
  Serial.write(HighByte);
  Serial.write(LowByte);
  delay(500);
}
