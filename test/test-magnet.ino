// Pines de control para el L298N
const int IN1 = 9;
const int IN2 = 10;

void setup() {
  Serial.begin(9600);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  
  // Estado inicial: Apagado
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  
  Serial.println("Control de Imán via L298N listo.");
}

void loop() {
  if (Serial.available() > 0) {
    char comando = Serial.read();

    if (comando == '1') { // ACTIVAR IMÁN
      digitalWrite(IN1, HIGH);
      digitalWrite(IN2, LOW);
      Serial.println("IMAN_STATUS: ACTIVADO");
    } 
    else if (comando == '0') { // DESACTIVAR IMÁN
      digitalWrite(IN1, LOW);
      digitalWrite(IN2, LOW);
      Serial.println("IMAN_STATUS: APAGADO");
    }
  }
}