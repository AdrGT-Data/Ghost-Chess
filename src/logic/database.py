import sqlite3
import os
import time
import math

"""
Este módulo contiene la clase DatabaseManager, que se encarga de gestionar la base de datos SQLite para almacenar la telemetría de las partidas de ajedrez simuladas.
La base de datos contiene dos tablas principales:
1. PARTIDAS: almacena información general de cada partida (fecha, dificultad, resultado).
2. TELEMETRIA_TURNOS: almacena información detallada de cada turno (jugador, movimiento, estado del tablero, tiempo de cálculo, distancia recorrida por el imán, tiempo que el imán estuvo encendido).
"""

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
        Crea las tablas relacionales.
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
                distancia_mm REAL,
                tiempo_iman_ms REAL,
                indice_termico REAL,
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
        
        # Obtenemos el ID que SQLite acaba de autogenerar y lo retornamos para usarlo en los turnos
        id_partida_actual = self.cursor.lastrowid
        
        return id_partida_actual

    def registrar_turno(self, id_partida, numero_turno, jugador, movimiento_uci, 
                        estado_fen, tiempo_calculo_ms, distancia_mm, tiempo_iman_ms, indice_termico):
        """
        Inserta un evento en Telemetria_Turnos vinculado a la partida actual.
        """
        query = '''
            INSERT INTO Telemetria_Turnos (
                id_partida, numero_turno, jugador, movimiento_uci, 
                estado_fen, tiempo_calculo_ms, distancia_mm, tiempo_iman_ms, indice_termico
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        valores = (id_partida, numero_turno, jugador, movimiento_uci, 
                   estado_fen, tiempo_calculo_ms, distancia_mm, tiempo_iman_ms, indice_termico)
        
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
            # Solo nos interesan las instrucciones de movimiento lineal (G0 y G1)
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

    def calcular_indice_termico(self, id_partida, numero_turno, temperatura_ambiente = 25, k_cool= 0.05, k_heat = 2.5):
        """
        Calcula un índice térmico simple basado en el tiempo que el imán estuvo encendido y el tiempo de cálculo de la IA.
        Este índice es una métrica inventada para evaluar la "carga térmica" del sistema.
        """

        # Recuperamos los datos del turno desde la base de datos
        tiempo_calculo_ms, tiempo_iman_ms = None, None
        self.cursor.execute("""
            SELECT tiempo_calculo_ms, tiempo_iman_ms 
            FROM Telemetria_Turnos 
            WHERE id_partida = ? AND numero_turno = ?
        """, (id_partida, numero_turno))

        actual_row = self.cursor.fetchone()

        if actual_row:
            tiempo_calculo_ms, tiempo_iman_ms = actual_row[0]/1000, actual_row[1]/1000
        else:
            raise ValueError(f"No se encontró el turno con id_partida = {id_partida} y numero_turno = {numero_turno}")

        if tiempo_calculo_ms <= 0 or tiempo_iman_ms < 0:
            raise ValueError("Valor temporal negativo")  


        # Para calcular la temperatura del turno anterior debemos recuperar el turno anterior
        temperatura_anterior = temperatura_ambiente  # Valor por defecto si no hay turno anterior
        self.cursor.execute("""
            SELECT indice_termico 
            FROM Telemetria_Turnos 
            WHERE id_partida = ? AND numero_turno = ?
        """, (id_partida, numero_turno - 1))

        previous_row = self.cursor.fetchone()
        if previous_row:
            temperatura_anterior = previous_row[0]


        # 1. Si el imán esta apagado pierde calor por una fórmula simple
        temperatura_apagado = temperatura_ambiente + (temperatura_anterior - temperatura_ambiente) * math.exp(-k_cool * tiempo_calculo_ms)

        # 2. Si el imán esta encendido, sube la temperatura según el tiempo de cálculo de la IA
        temperatura_encendido = temperatura_apagado + k_heat * tiempo_iman_ms

        return temperatura_encendido

    def close(self):
        self.conn.close()

# Pequeño bloque de prueba para generar la base de datos al ejecutar este script
if __name__ == "__main__":
    db = DatabaseManager()
    db.close()