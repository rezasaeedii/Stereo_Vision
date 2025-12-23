#define PIN1 D2
#define PIN2 D3
#define PIN3 D4
#define PIN4 D5

void setup() {
  Serial.begin(115200);
  pinMode(PIN1, INPUT);
  pinMode(PIN2, INPUT);
  pinMode(PIN3, INPUT);
  pinMode(PIN4, INPUT);
}

void loop() {
  int val1 = digitalRead(PIN1);
  int val2 = digitalRead(PIN2);
  int val3 = digitalRead(PIN3);
  int val4 = digitalRead(PIN4);

  Serial.print("Pin1: "); Serial.print(val1);
  Serial.print(" | Pin2: "); Serial.print(val2);
  Serial.print(" | Pin3: "); Serial.print(val3);
  Serial.print(" | Pin4: "); Serial.println(val4);

  delay(500);
}
