const int CDS_PIN = A0;   

void setup() {
  Serial.begin(9600);       
  pinMode(CDS_PIN, INPUT);  
}

void loop() {
  Serial.println(analogRead(CDS_PIN));  
  delay(100);
}
