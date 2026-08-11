import sqlite3
import os
import time
import math

class DatabaseManager:
    def __init__(self, db_name="ghost_chess_telemetry.db"):
        """
        Inicializa la conexión y asegura que el esquema exista.
        """
        # Creamos una carpeta data si no existe para mantener el proyecto limpio
        self.db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
        # Si la carpeta ya esta creada, no hacemos nada. Si no, la creamos.
        os.makedirs(self.db_dir, exist_ok=True)

        # Definimos la ruta completa de la base de datos
        self.db_path = os.path.join(self.db_dir, db_name)
        # Conectamos a la base de datos (se crea si no existe)
        self.conn = sqlite3.connect(self.db_path)
        # Creamos un cursor para ejecutar comandos SQL
        self.cursor = self.conn.cursor()
        
        self._create_tables()

    def _create_tables(self):
        """
        Ejecuta el DDL para crear las tablas relacionales.
        """

        # Entidad Partidas: almacena información general de cada partida
        # Entidad Telemetria_Turnos: almacena información detallada de cada turno
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS PARTIDAS (
                id_partida INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_inicio DATETIME DEFAULT CURRENT_TIMESTAMP,
                dificultad_ia INTEGER,
                resultado TEXT DEFAULT 'En curso'
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS TELEMETRIA_TURNOS (
                id_turno INTEGER PRIMARY KEY AUTOINCREMENT,
                id_partida INTEGER,
                numero_turno INTEGER,
                jugador TEXT,
                movimiento_uci TEXT,
                estado_fen TEXT,
                tiempo_calculo_ms REAL,
                distancia_gcode_mm REAL,
                tiempo_iman_ms REAL,
                FOREIGN KEY(id_partida) REFERENCES PARTIDAS(id_partida)
            )
        ''')

        # Guardamos los cambios y confirmamos que la base de datos está lista
        self.conn.commit()
        print(f"Base de datos operativa en: {self.db_path}")

    def iniciar_partida(self, dificultad_ia):
        """
        Crea una nueva fila en PARTIDAS al iniciar el programa.
        Retorna el id_partida autogenerado para usarlo en los turnos.
        """
        query = '''
            INSERT INTO PARTIDAS (dificultad_ia)
            VALUES (?)
        '''
        # Ejecutamos el insert pasando la dificultad como tupla
        self.cursor.execute(query, (dificultad_ia,))
        self.conn.commit()
        
        # MAGIA SQL: Obtenemos el ID que SQLite acaba de autogenerar
        id_partida_actual = self.cursor.lastrowid
        print(f"--- Telemetría: Iniciada Partida ID {id_partida_actual} ---")
        
        return id_partida_actual

    def registrar_turno(self, id_partida, numero_turno, jugador, movimiento_uci, 
                        estado_fen, tiempo_calculo_ms, distancia_gcode_mm, tiempo_iman_ms):
        """
        Inserta un evento en Telemetria_Turnos vinculado a la partida actual.
        """
        query = '''
            INSERT INTO Telemetria_Turnos (
                id_partida, numero_turno, jugador, movimiento_uci, 
                estado_fen, tiempo_calculo_ms, distancia_gcode_mm, tiempo_iman_ms
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        valores = (id_partida, numero_turno, jugador, movimiento_uci, 
                   estado_fen, tiempo_calculo_ms, distancia_gcode_mm, tiempo_iman_ms)
        
        self.cursor.execute(query, valores)
        self.conn.commit()

    def calcular_distancia_gcode(self, gcode_list):
        """
        Calcula la distancia total en mm que recorrerá el robot según las instrucciones G-code.
        gcode_instructions: lista de strings con instrucciones G-code (ej: ["G1 X10 Y20", "G1 X15 Y25"])
        """
        total_distance = 0.0
        last_x, last_y = None, None

        for instruction in gcode_list:
            # Solo nos interesan las instrucciones de movimiento (G0 y G1)
            if instruction.startswith("G0") or instruction.startswith("G1"):
                parts = instruction.split()
                x, y = None, None

                for part in parts:
                    if part.startswith("X"):
                        x = float(part[1:])
                    elif part.startswith("Y"):
                        y = float(part[1:])

                # SI tenemos coordenadas válidas, calculamos la distancia
                if x is not None and y is not None:
                    if last_x is not None and last_y is not None:
                        dx = x - last_x
                        dy = y - last_y
                        distance = math.sqrt(dx**2 + dy**2)
                        total_distance += distance
                    
                    last_x, last_y = x, y

        return total_distance

    def calcular_tiempo_iman(self, distancia_mm, velocidad_mm_s=50.0):
        """
        Calcula el tiempo estimado que tardará el imán en mover la pieza según la distancia.
        velocidad_mm_s: velocidad promedio del imán en mm/s (ajustable según pruebas)
        """
        if velocidad_mm_s <= 0:
            raise ValueError("La velocidad debe ser mayor que cero.")
        
        tiempo_segundos = distancia_mm / velocidad_mm_s
        return tiempo_segundos * 1000  # Convertimos a milisegundos

    def close(self):
        self.conn.close()

# Pequeño bloque de prueba para generar la base de datos al ejecutar este script
if __name__ == "__main__":
    db = DatabaseManager()
    db.close()