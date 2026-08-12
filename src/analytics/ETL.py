import sqlite3
import pandas as pd
import os

def cargar_datos():
    # Extracción de datos desde la base de datos SQLite a un DataFrame de Pandas para análisis posterior.
    # Aseguramos la ruta correcta al archivo .db
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "ghost_chess_telemetry.db")
    
    # 1. Abrimos conexión de lectura
    conn = sqlite3.connect(db_path)
    
    # 2. Consultas SQL directas a Pandas DataFrames
    df_partidas = pd.read_sql_query("SELECT * FROM Partidas", conn)
    df_turnos = pd.read_sql_query("SELECT * FROM Telemetria_Turnos", conn)
    
    conn.close()
    
    # 3. Transformación: Unimos las tablas (Equivalente a un LEFT JOIN en SQL)
    # Así cada turno sabe a qué nivel de dificultad se jugó y cómo acabó la partida
    df_final = pd.merge(df_turnos, df_partidas, on="id_partida", how="left")
    
    # 4. Limpieza básica: Convertimos la fecha de string a formato Datetime real de Pandas
    df_final['fecha_inicio'] = pd.to_datetime(df_final['fecha_inicio'])
    
    return df_final

if __name__ == "__main__":
    df = cargar_datos()
    
    # Un pequeño vistazo a los datos para confirmar que todo está en orden
    print("\nDesgaste mecánico total:")
    print(f"{df['distancia_gcode_mm'].sum() / 1000} m")
    print("\nTiempo total de imán encendido(Riesgo térmico):")
    print(f"{(df['tiempo_iman_ms'].sum() / 1000) / 3600} h")