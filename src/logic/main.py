from chess_engine import GhostChessEngine
from communication import SerialComunicator
from simulation import MagnetSimulator 
import chess


def main():
    # 1. SETUP
    sim = MagnetSimulator()

    game = GhostChessEngine(difficulty=1)

    situacion_fen = "7k/4P3/8/8/8/8/8/K7 w - - 0 1"
    game.board.set_fen(situacion_fen)

    sim.draw_pieces(game.board)
    #arduino = SerialComunicator(port='/dev/ttyUSB0', baudrate=115200) 

    while not game.board.is_game_over():
        # 2. IA PENSANDO
        best_move = game.get_best_move()

        processed_gcode = game.process_full_move(best_move)

        game.play_move(best_move)

        # 2.1 Simulación visual del movimiento de la IA
        sim.simulate_gcode(processed_gcode)
        sim.draw_pieces(game.board)  # Actualizamos la visualización del tablero después del movimiento de la IA

        # 3. JUGADA HUMANA
        # Pedimos al jugador que introuzca su jugada en formato UCI (ej: e2e4)
        while True:
            human_move_input = input("Introduce tu jugada (formato UCI, ej: e7e5): ")

            #Quitamos los espacios ineccesarios
            human_move_input = human_move_input.strip() 
            
            try:
                # Intentamos traducir el texto a un objeto Move
                human_move = chess.Move.from_uci(human_move_input)
                
                # Verificamos si es legal en el ESTADO ACTUAL del tablero
                if human_move in game.board.legal_moves:

                    gcode_human = game.process_full_move(human_move)
                    sim.simulate_gcode(gcode_human)
                    game.play_move(human_move)  # Actualizamos el estado con la jugada humana
                    sim.draw_pieces(game.board)  # Actualizamos la visualización del tablero después de
                    


                    # 2. Respuesta automática de la IA
                    print(f"\n--- TURNO IA ---")
                    best_move = game.get_best_move()
                    gcode_ia = game.process_full_move(best_move)
                    sim.simulate_gcode(gcode_ia)
                    game.board.push(best_move)
                    sim.draw_pieces(game.board)
                else:
                    print("Movimiento invalido. Intenta de nuevo.")
                    
            except ValueError:
                # Atrapamos el error si el usuario escribe un formato que no es UCI (ej: "hola", "peon a4")
                print("Formato incorrecto. Introduce el formato UCI de origen y destino (ej: e7e5).")


    #gcode = game.process_full_move(best_move)

    # 3. ACCIÓN 
    #arduino.connect()
    #arduino.send_gcode(gcode)
    #arduino.disconnect()
    sim.screen.exitonclick()  # Cierra la ventana de simulación al hacer clic
    game.close()

if __name__ == "__main__":
    main()





