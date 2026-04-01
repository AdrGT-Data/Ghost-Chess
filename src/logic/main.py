from chess_engine import GhostChessEngine
from communication import SerialCommunicator
import chess


def main():
    # 1. SETUP
    game = GhostChessEngine()
    
    arduino = SerialCommunicator(port='/dev/ttyACM0') 
    
    # 2. IA PENSANDO
    best_move = game.get_best_move()
    gcode = game.process_full_move(best_move)

    # 3. ACCIÓN (Aquí es donde ocurre la magia el viernes)
    arduino.connect()
    arduino.send_gcode(gcode)
    arduino.disconnect()

    game.close()

if __name__ == "__main__":
    main()
















"""
if __name__ == "__main__":
    game = GhostChessEngine()
    
    # CASO 1: Movimiento sugerido por la IA (normalmente un Peón al inicio)
    best = game.get_best_move()
    path_ia = game.generate_robot_path(best)
    print(f"Ruta IA ({best}): {path_ia}")
    
    # CASO 2: Forzamos un Caballo (G1 a F3) para ver la evasión
    knight_move = chess.Move.from_uci("g1f3")
    path_knight = game.generate_robot_path(knight_move)
    print(f"\nRuta Caballo (g1f3): {path_knight}")
    
    game.close()

    

        # 1. Ver tablero inicial
    print("\nTablero Lógico:\n", game.board)
    
    # 2. Consultar a la IA
    best_move = game.get_best_move()  # Mejor movimiento posible según Stockfish
    origin, target = game.translate_to_matrix(best_move)  # Coordenadas

    print(f"\n Movimiento: {best_move}")
    print(f" Coordenadas para el imán: Origen {origin} -> Destino {target}")

    # 3. Detectar qué estamos moviendo
    piece_name = game.get_piece_at(best_move.from_square)
    print(f" Pieza detectada: {piece_name}")

    # 4. Actualizar el tablero para la siguiente jugada
    game.play_move(best_move)
    print("\nTablero después del movimiento:\n", game.board)
    
    # 5. Planificar la ruta física
    path = game.plan_path(best_move)
    print(f"\n Plan de ruta del imán:")
    for i, step in enumerate(path):
        print(f"   Paso {i}: {step}")

    game.close()

"""