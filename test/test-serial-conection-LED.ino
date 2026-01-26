const int ledExterno = 13; // Usamos el 13 porque activa el externo y el de la placa a la vez

void setup() {
  Serial.begin(9600); // Iniciamos el canal de comunicación
  pinMode(ledExterno, OUTPUT);
  digitalWrite(ledExterno, LOW); // Empezamos apagados
  Serial.println("Sistema de LED listo.");
}

void loop() {
  if (Serial.available() > 0) {
    char comando = Serial.read();
    
    if (comando == '1') { // Enviamos un '1' para encender
      digitalWrite(ledExterno, HIGH);
      Serial.println("LED: ENCENDIDO");
    } 
    else if (comando == '0') { // Enviamos un '0' para apagar
      digitalWrite(ledExterno, LOW);
      Serial.println("LED: APAGADO");
    }
  }
}
