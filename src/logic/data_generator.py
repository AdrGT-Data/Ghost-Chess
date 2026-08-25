import time
import chess
from chess_engine import GhostChessEngine
from database import DatabaseManager
import math
import numpy as np

"""
Este script simula partidas de ajedrez entre dos inteligencias artificiales (IA) y registra la telemetría de cada turno en una base de datos SQLite.
Cada partida se juega hasta que haya jaque mate o tablas, y se almacena información detallada de cada turno, incluyendo el jugador, el movimiento realizado, el estado del tablero en formato FEN, el tiempo de cálculo de la IA, la distancia recorrida por el imán y el tiempo que el imán estuvo encendido.
El objetivo es generar datos de telemetría que luego puedan ser analizados para estudiar el comportamiento
"""

def simular_salto_termico(temp_anterior, tiempo_calculo_ms, tiempo_iman_ms):
    """Calcula el nuevo ICT puramente en memoria."""
    t_off = tiempo_calculo_ms / 1000.0
    t_on = tiempo_iman_ms / 1000.0
    
    # Constantes térmicas (ajustables)
    T_AMB = 25.0
    K_COOL = 0.05
    K_HEAT = 2.5
    
    # 1. Enfriamiento durante la reflexión
    temp_apagado = T_AMB + (temp_anterior - T_AMB) * math.exp(-K_COOL * t_off)
    
    # 2. Calentamiento durante el movimiento
    temp_nueva = temp_apagado + (K_HEAT * t_on)
    
    return round(temp_nueva, 2)


def simular_partidas(num_partidas=5):

    # 1. Iniciamos el motor de ajedrez y la base de datos
    game = GhostChessEngine()
    db = DatabaseManager()
    
    for i in range(num_partidas):
        # Reiniciamos el tablero lógico para cada partida nueva
        game.board.reset() 
        id_partida = db.iniciar_partida(dificultad_ia=5)
        turno_contador = 1
        
        print(f"Procesando Partida {i+1}/{num_partidas} (ID BBDD: {id_partida})...")

        temp_iman = 25.0  # Temperatura inicial del imán
        
        # Bucle de juego: sigue hasta que haya jaque mate o tablas
        while not game.board.is_game_over():
            # Determinar a quién le toca
            jugador_actual = "IA_Blancas" if game.board.turn == chess.WHITE else "IA_Negras"
            
            # Simulamos un tiempo aleatorio 
            tiempo_simulado = np.random.randint(3000, 35000)  # Entre 3 y 35 segundos

            best_move = game.get_best_move(limit_time=0.01) 
                        
            # Extraemos telemetría física
            gcode = game.process_full_move(best_move)
            distancia = db.calcular_distancia_gcode(gcode)
            tiempo_iman = db.calcular_tiempo_iman(distancia)

            # Calculamos el índice térmico basado en el turno anterior
            temp_iman = simular_salto_termico(
                temp_anterior=temp_iman,
                tiempo_calculo_ms=tiempo_simulado,
                tiempo_iman_ms=tiempo_iman
            )
            
            # Ingesta en la Base de Datos
            db.registrar_turno(
                id_partida=id_partida,
                numero_turno=turno_contador,
                jugador=jugador_actual,
                movimiento_uci=best_move.uci(),
                estado_fen=game.board.fen(),
                tiempo_calculo_ms=tiempo_simulado,
                distancia_mm=distancia,
                tiempo_iman_ms=tiempo_iman,
                indice_termico=temp_iman
            )
            
            # Ejecutamos el movimiento matemáticamente
            game.board.push(best_move)
            turno_contador += 1
            
        # Al terminar la partida, actualizamos el resultado final
        resultado_final = game.board.result() # Devuelve '1-0', '0-1' o '1/2-1/2'
        db.cursor.execute("UPDATE Partidas SET resultado = ? WHERE id_partida = ?", (resultado_final, id_partida))
        db.conn.commit()
        
        print(f"  -> Partida {i+1} completada. Resultado: {resultado_final}. Turnos totales: {turno_contador}")
        
    game.close()
    db.close()
    print("\nSIMULACIÓN FINALIZADA")

if __name__ == "__main__":
    simular_partidas(num_partidas=4)