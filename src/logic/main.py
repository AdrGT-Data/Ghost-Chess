from chess_engine import GhostChessEngine
from communication import SerialComunicator
from simulation import MagnetSimulator 
from database import DatabaseManager
import chess
import time

def main():
    # 1. SETUP
    sim = MagnetSimulator()

    game = GhostChessEngine(difficulty=1)

    #Incializamos la base de datos y creamos una nueva partida
    db = DatabaseManager()
    id_partida = db.iniciar_partida(dificultad_ia=5)
    turnos = 0

    sim.draw_pieces(game.board)
    #arduino = SerialComunicator(port='/dev/ttyUSB0', baudrate=115200) 

    while not game.board.is_game_over():

        try:
            # 2. ----------------------JUGADA IA-------------------------

            print(f"\n--- TURNO IA ---")

            #Disparamos el cronómetro
            inicio_calculo_ia = time.time()

            best_move = game.get_best_move()

            #Detenemos el cronómetro
            fin_calculo_ia = time.time()
            tiempo_calculo_ia_ms = (fin_calculo_ia - inicio_calculo_ia) * 1000  # Convertimos a milisegundos

            processed_gcode = game.process_full_move(best_move)

            game.play_move(best_move)

            # 2.1 Simulación visual del movimiento de la IA
            sim.simulate_gcode(processed_gcode)
            sim.draw_pieces(game.board)  # Actualizamos la visualización del tablero después del movimiento de la IA

            # 2.2 Registro de la jugada de la IA en la base de datos
            distancia_gcode_mm_ia = db.calcular_distancia_gcode(processed_gcode)
            db.registrar_turno(
                id_partida=id_partida,
                numero_turno=turnos,
                jugador="IA_Blancas",
                movimiento_uci=best_move.uci(), # Extraemos el texto
                estado_fen=game.board.fen(),    # Extraemos la foto FEN actual
                tiempo_calculo_ms=tiempo_calculo_ia_ms,          # Usamos el tiempo calculado
                distancia_gcode_mm=distancia_gcode_mm_ia,      #Calculamos distancia recorrida por el imán en mm 
                tiempo_iman_ms=db.calcular_tiempo_iman(distancia_gcode_mm_ia)              # Calculamos el tiempo que ha tardado el imán en recorrer la distancia
            )
            turnos += 1

            # 3. ------------------------------JUGADA HUMANA------------------------------

            # Disparamos cronómetro para medir el tiempo de entrada del jugador
            inicio_entrada_humana = time.time()

            # Pedimos al jugador que introuzca su jugada en formato UCI (ej: e2e4)
            human_move_input = input("Introduce tu jugada (formato UCI, ej: e7e5): ")

            #Quitamos los espacios ineccesarios
            human_move_input = human_move_input.strip() 
            
            # Traducimos el texto a un objeto Move de python-chess
            human_move = chess.Move.from_uci(human_move_input)
                
            # Verificamos si es legal en el ESTADO ACTUAL del tablero
            if human_move in game.board.legal_moves:

                # Paramos el cronómetro para medir el tiempo de entrada del jugador
                fin_entrada_humana = time.time()
                tiempo_entrada_humana_ms = (fin_entrada_humana - inicio_entrada_humana) * 1000  # Convertimos a milisegundos

                #Movimiento humano válido, procesamos y simulamos
                gcode_human = game.process_full_move(human_move)
                sim.simulate_gcode(gcode_human)
                game.play_move(human_move)  # Actualizamos el estado con la jugada humana
                sim.draw_pieces(game.board)  # Actualizamos la visualización del tablero después de
                    
                # Registramos el turno humano en la base de datos
                distancia_gcode_mm_humano = db.calcular_distancia_gcode(gcode_human)
                db.registrar_turno(
                    id_partida=id_partida,
                    numero_turno=turnos,
                    jugador="Humano_Negras",
                    movimiento_uci=human_move.uci(), # Extraemos el texto
                    estado_fen=game.board.fen(),    # Extraemos la foto FEN actual
                    tiempo_calculo_ms=tiempo_entrada_humana_ms,          # Usamos el tiempo calculado
                    distancia_gcode_mm=distancia_gcode_mm_humano,         # Ignorado por hoy
                    tiempo_iman_ms=db.calcular_tiempo_iman(distancia_gcode_mm_humano)              # Ignorado por hoy
                )
                turnos += 1

            else:
                print("Movimiento invalido. Intenta de nuevo.")
                    
        except ValueError:
            # Atrapamos el error si el usuario escribe un formato que no es UCI (ej: "hola", "peon a4")
            print("Formato incorrecto. Introduce el formato UCI de origen y destino (ej: e7e5).")


    #gcode = game.process_full_move(best_move)

    # 3. Comunicación con Arduino (desactivada por ahora)
    #arduino.connect()
    #arduino.send_gcode(gcode)
    #arduino.disconnect()

    # CIERRE DE LA SIMULACIÓN Y DEL MOTOR
    db.cursor.execute("UPDATE Partidas SET resultado = 'Finalizada' WHERE id_partida = ?", (id_partida,))
    db.conn.commit()
    db.close()
    
    sim.screen.exitonclick()  # Cierra la ventana de simulación al hacer clic
    game.close()

if __name__ == "__main__":
    main()





