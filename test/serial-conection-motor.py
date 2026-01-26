import serial
import time

# Configura el puerto correcto (/dev/ttyUSB0 en Linux)
PUERTO = '/dev/ttyUSB0'
BAUDIOS = 9600

try:
    # Inicializamos la conexión
    arduino = serial.Serial(PUERTO, BAUDIOS, timeout=1)
    time.sleep(2)  # Pausa necesaria para que el Arduino se resetee al conectar
    print(f"--- Conectado con éxito a {PUERTO} ---")

    while True:
        print("\nComandos: [F: Adelante] [B: Atrás] [S: Parar] [Q: Salir]")
        accion = input("Introduce una orden: ").upper()

        if accion == 'Q':
            arduino.write(b'S') # Seguridad: paramos el motor antes de cerrar
            break
        
        if accion in ['F', 'B', 'S']:
            # Enviamos el comando codificado en bytes
            arduino.write(accion.encode())
            
            # Leemos la confirmación que nos devuelve el Arduino
            time.sleep(0.1)
            respuesta = arduino.readline().decode('utf-8').strip()
            if respuesta:
                print(f"Respuesta del hardware: {respuesta}")
        else:
            print("⚠️ Comando no reconocido. Usa F, B o S.")

    arduino.close()
    print("Conexión cerrada.")

except Exception as e:
    print(f"❌ Error de conexión: {e}")