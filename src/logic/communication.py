import serial
import time

class SerialComunicator:
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600, timeout = 1):
        """Inicializa la conexión serie con Arduino"""
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection = None
    
    def connect(self):
        try:
            self.connection = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            time.sleep(2)  # Espera a que Arduino se resetee al conectar
            print(f"Conectado con éxito a {self.port}")
        except Exception as e:
            print(f"Error al conectar al puerto serie: {e}")

    def send_gcode(self, gcode_list):
        """Envía una lista de comandos y espera el ok de Arduino"""
        if not self.connection:
            print("No hay conexión, abortando...")
            return
        
        for line in gcode_list:
            clean_line = line.split(';') [0].strip() #Quitamos comentarios
            if not clean_line: continue

            print(f"Enviando: {clean_line}...", end=" ")
            self.connection.write((clean_line + '\n').encode('utf-8'))
            
            # Esperar respuesta del Arduino
            while True:
                response = self.connection.readline().decode('utf-8').strip()
                if response.upper() == "OK":
                    print("¡Recibido OK!")
                    break
                time.sleep(0.1)
    
    def disconnect(self):
        if self.connection:
            self.connection.close()
            print("Puerto serie cerrado")
