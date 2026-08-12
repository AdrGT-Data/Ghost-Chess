import time
import chess
from chess_engine import GhostChessEngine
from database import DatabaseManager

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
        
        # Bucle de juego: sigue hasta que haya jaque mate o tablas
        while not game.board.is_game_over():
            # Determinar a quién le toca
            jugador_actual = "IA_Blancas" if game.board.turn == chess.WHITE else "IA_Negras"
            
            # Cronometramos (le damos muy poco tiempo para que mueva casi al instante)
            inicio_reloj = time.time()
            best_move = game.get_best_move(limit_time=0.01) 
            fin_reloj = time.time()
            tiempo_ms = round((fin_reloj - inicio_reloj) * 1000, 2)
            
            # Extraemos telemetría física
            gcode = game.process_full_move(best_move)
            distancia = db.calcular_distancia_gcode(gcode)
            tiempo_iman = db.calcular_tiempo_iman(distancia)
            
            # Ingesta en la Base de Datos
            db.registrar_turno(
                id_partida=id_partida,
                numero_turno=turno_contador,
                jugador=jugador_actual,
                movimiento_uci=best_move.uci(),
                estado_fen=game.board.fen(),
                tiempo_calculo_ms=tiempo_ms,
                distancia_gcode_mm=distancia,
                tiempo_iman_ms=tiempo_iman
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