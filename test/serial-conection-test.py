import serial
import time

# Configura tu puerto. Si no es /dev/ttyUSB0, verifícalo en el Arduino IDE
puerto = "/dev/ttyUSB0"

try:
    arduino = serial.Serial(puerto, 9600, timeout=1)
    time.sleep(2)  # Tiempo para que el Arduino se estabilice
    print("--- Control de LED iniciado ---")

    while True:
        opcion = input("Escribe '1' para encender, '0' para apagar o 'q' para salir: ")
        
        if opcion.lower() == 'q':
            break
        
        if opcion in ["1", "0"]:
            arduino.write(opcion.encode()) # Enviamos el carácter como bytes
            time.sleep(0.1)
            respuesta = arduino.readline().decode('utf-8').strip()
            print(f"Respuesta: {respuesta}")
        else:
            print("Entrada no válida.")

    arduino.close()
    print("Conexión finalizada.")

except Exception as e:
    print(f"Error detectado: {e}")