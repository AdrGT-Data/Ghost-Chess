import serial
import time

# Verifica si tu puerto es /dev/ttyUSB0
PUERTO = '/dev/ttyUSB0'

try:
    arduino = serial.Serial(PUERTO, 9600, timeout=1)
    time.sleep(2) 
    print(f"Conectado al sistema de imán en {PUERTO}")

    while True:
        accion = input("\nControl: [1] Encender | [0] Apagar | [Q] Salir: ").lower()

        if accion == 'q':
            arduino.write(b'0')
            break
        
        if accion in ['1', '0']:
            arduino.write(accion.encode())
            time.sleep(0.1)
            # Escuchamos la confirmación del Arduino
            print(f"Hardware dice: {arduino.readline().decode('utf-8').strip()}")
        else:
            print("Comando inválido.")

    arduino.close()
    print("Conexión finalizada.")

except Exception as e:
    print(f"Error en la comunicación: {e}")