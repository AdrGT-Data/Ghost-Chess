import chess
import chess.engine

class GhostChessEngine:


    #------------------------------INICIALIZACION------------------------------------    
    
    def __init__(self, engine_path="/usr/games/stockfish"):
        """Inicializa el motor Stockfish y el tablero lógico."""
        self.SQUARE_SIZE_MM = 50 # Lado físico que tendra cada cuadrado del tablero
        self.BOARD_SIZE_MM = 400 # Lado total tablero
        self.GRAVEYARD_X = -50 # Fuera del tablero a la izda
        self.GRAVEYARD_Y = 100
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)
            self.board = chess.Board()
            print("Motor Stockfish despertado correctamente.")

        except Exception as e:
            print(f"Error al iniciar Stockfish: {e}")

    #------------------------------------APAGAR-----------------------------------------
    
    def close(self):
        """Apaga el motor de forma segura."""
        self.engine.quit()

    #------------------------------------ATRIBUTOS--------------------------------------------
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

    def format_gcode(self, command, x, y, speed=3000):
        """Devuelve una línea de G-Code formateada."""
        # G0 es rápido (vacío), G1 es lineal (con pieza)
        return f"{command} X{x:.2f} Y{y:.2f} F{speed}"
    




    def process_full_move (self, move):
        """Coordina el movimiento completo"""
        instructions= []
        origin, target = self.translate_to_matrix(move)

        # 1. ¿Hay eliminación de pieza?
        if self.get_piece_at(move.to_square) != "EMPTY" :
            # La dirección destino tiene una pieza, hay eliminación
            instructions.append("; --- FASE: RETIRAR PIEZA ---")

            mm_x, mm_y = self.to_real_mm(target) #COnvertimos el target en mm

            instructions.append("; --- INICIO FASE CAPTURA ---")
            instructions.append(self.format_gcode("G0", mm_x, mm_y)) # Ir al enemigo
            instructions.append("M3 ; MAGNET ON")
            instructions.append(self.format_gcode("G1", self.GRAVEYARD_X, self.GRAVEYARD_Y)) # Al cementerio
            instructions.append("M5 ; MAGNET OFF")
            instructions.append("; --- FIN FASE CAPTURA ---")
        

        # 2. Una vez eliminada la pieza, movemos la pieza
        path = self.plan_path(move)
        instructions.append("; ---INICIO MOVIMIENTO PIEZA ---")

        orig_mm_x, orig_mm_y = self.to_real_mm(path[0]) # Punto origen en mm

        instructions.append(self.format_gcode("G0", orig_mm_x, orig_mm_y))
        instructions.append("M3 ; MAGNET ON")

        # Recorremos los puntos intermedios 
        for step in path[1:]:
            step_x, step_y = self.to_real_mm(step)
            instructions.append(self.format_gcode("G1", step_x, step_y))
        
        instructions.append("M5 ; MAGNET OFF")

        return instructions



