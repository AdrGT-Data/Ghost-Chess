import chess
import chess.engine

class GhostChessEngine:
    def __init__(self, engine_path="/usr/games/stockfish"):
        """Inicializa el motor Stockfish y el tablero lógico."""
        self.SQUARE_SIZE_M = 50 # Lado físico que tendra cada cuadrado del tablero
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)
            self.board = chess.Board()
            print("Motor Stockfish despertado correctamente.")
        except Exception as e:
            print(f"Error al iniciar Stockfish: {e}")

    def to_real_mm(self, logical_coords):
        """Convierte (X, Y) lógico a (X_mm, Y_mm) reales."""
        x, y = logical_coords
        return (x * self.SQUARE_SIZE_MM + 25, y * self.SQUARE_SIZE_MM + 25)

    def get_best_move(self, limit_time=0.1):
        """Pide a la IA el mejor movimiento."""
        result = self.engine.play(self.board, chess.engine.Limit(time=limit_time))
        return result.move

    def translate_to_matrix(self, move):
        """Convierte jugadas de ajedrez a coordenadas (X, Y)"""
        # square_file: 0-7 (a-h) | square_rank: 0-7 (1-8)
        from_x = chess.square_file(move.from_square)
        from_y = chess.square_rank(move.from_square)
        
        to_x = chess.square_file(move.to_square)
        to_y = chess.square_rank(move.to_square)
        
        return (from_x, from_y), (to_x, to_y)

    def play_move(self, move):
        """Actualiza el estado interno del juego."""
        self.board.push(move)

    def close(self):
        """Apaga el motor de forma segura."""
        self.engine.quit()

    def get_piece_at(self, square):
        """Devuelve el tipo de pieza en una casilla dada (ej: Peón, Caballo...)."""
        piece = self.board.piece_at(square)
        if piece:
            # Retorna el nombre de la pieza: PAWN, KNIGHT, BISHOP, etc.
            return chess.piece_name(piece.piece_type).upper()
        return "EMPTY"

    def is_path_clear(self, move):
        """
        Analiza si hay piezas en el camino de un movimiento rectilíneo.
        Nota: El Caballo siempre devuelve False porque 'salta'.
        """
        # Si es un Caballo, siempre asumimos que el camino está bloqueado físicamente
        if self.get_piece_at(move.from_square) == "KNIGHT":
            return False
            
        # Para Peones, Torres, Alfiles y Reinas, revisamos las casillas intermedias
        # python-chess ya tiene una función para esto
        path_indices = chess.SquareSet(chess.between(move.from_square, move.to_square))
        
        for square in path_indices:
            if self.board.piece_at(square) is not None:
                return False # ¡Hay un obstáculo!
                
        return True # Camino despejado

    def plan_path(self, move):
        """
        Genera una lista de coordenadas (X, Y) que el imán debe seguir.
        """
        origin, target = self.translate_to_matrix(move)
        
        if self.is_path_clear(move):
            # Ruta simple: solo origen y destino
            return [origin, target]
        else:
            # Ruta de evasión: usamos los 'bordes'
            # Ejemplo simplificado: mover a la intersección por las líneas
            # Paso 1: Salir al borde horizontal (Y + 0.5)
            waypoint1 = (origin[0] + 0.5, origin[1] + 0.5)
            # Paso 2: Ir hasta la columna del destino por la línea
            waypoint2 = (target[0] + 0.5, origin[1] + 0.5)
            # Paso 3: Ir hasta la fila del destino por la línea
            waypoint3 = (target[0] + 0.5, target[1] + 0.5)
            
            return [origin, waypoint1, waypoint2, waypoint3, target]

    def generate_robot_path(self, move):
        """
        Determina si el movimiento es directo o requiere ruta de evasión.
        Retorna una lista de tuplas [(x1, y1), (x2, y2), ...]
        """
        origin, target = self.translate_to_matrix(move)
        piece = self.get_piece_at(move.from_square)

        # Si el camino está despejado (is_path_clear) y NO es un Caballo
        if self.is_path_clear(move) and piece != "KNIGHT":
            print(f"🔹 Movimiento directo para {piece}")
            return [origin, target]
        
        # Si hay obstáculos o es un Caballo, usamos la ruta por los bordes
        print(f"⚠️ Ruta de evasión activada para {piece}")
        
        # Ruta en 'L' por las líneas divisorias (intersecciones)
        # 1. Salir al borde de la casilla actual
        step1 = (origin[0] + 0.5, origin[1] + 0.5)
        # 2. Moverse horizontalmente por la línea hasta la columna destino
        step2 = (target[0] + 0.5, origin[1] + 0.5)
        # 3. Moverse verticalmente por la línea hasta la fila destino
        step3 = (target[0] + 0.5, target[1] + 0.5)
        # 4. Entrar al centro de la casilla destino
        
        return [origin, step1, step2, step3, target]



"""

if __name__ == "__main__":
    # Prueba de concepto
    game = GhostChessEngine()

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