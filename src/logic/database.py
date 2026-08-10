import sqlite3
import os

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
            CREATE TABLE IF NOT EXISTS Partidas (
                id_partida INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_inicio DATETIME DEFAULT CURRENT_TIMESTAMP,
                dificultad_ia INTEGER,
                resultado TEXT DEFAULT 'En curso'
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Telemetria_Turnos (
                id_turno INTEGER PRIMARY KEY AUTOINCREMENT,
                id_partida INTEGER,
                numero_turno INTEGER,
                jugador TEXT,
                movimiento_uci TEXT,
                estado_fen TEXT,
                tiempo_calculo_ms REAL,
                distancia_gcode_mm REAL,
                tiempo_iman_ms REAL,
                FOREIGN KEY(id_partida) REFERENCES Partidas(id_partida)
            )
        ''')

        # Guardamos los cambios y confirmamos que la base de datos está lista
        self.conn.commit()
        print(f"Base de datos operativa en: {self.db_path}")

    def iniciar_partida(self, dificultad_ia):
        """
        Crea una nueva fila en Partidas al iniciar el programa.
        Retorna el id_partida autogenerado para usarlo en los turnos.
        """
        query = '''
            INSERT INTO Partidas (dificultad_ia)
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

    def close(self):
        self.conn.close()

# Pequeño bloque de prueba para generar la base de datos al ejecutar este script
if __name__ == "__main__":
    db = DatabaseManager()
    db.close()