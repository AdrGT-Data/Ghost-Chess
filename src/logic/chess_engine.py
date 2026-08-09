from shutil import move

import chess
import chess.engine

class GhostChessEngine:


    #------------------------------INICIALIZACION------------------------------------    
    
    def __init__(self, engine_path="/usr/games/stockfish", difficulty=20):
        """Inicializa el motor Stockfish y el tablero lógico."""
        self.SQUARE_SIZE_MM = 50 # Lado físico que tendra cada cuadrado del tablero
        self.BOARD_SIZE_MM = 400 # Lado total tablero
        self.GRAVEYARD_X = -2 # Fuera del tablero a la izda
        self.GRAVEYARD_Y = 3
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)
            self.board = chess.Board()
            self.engine.configure({"Skill Level": difficulty})

            print("Motor Stockfish despertado correctamente.")

        except Exception as e:
            print(f"Error al iniciar Stockfish: {e}")

    #------------------------------------APAGAR-----------------------------------------
    
    def close(self):
        try:
            self.engine.quit()
            print("Motor Stockfish cerrado correctamente.")
        except Exception as e:
            print(f"Error al cerrar Stockfish: {e}")

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
    
    def translate_to_uci(self, from_coords, to_coords):
        """Convierte coordenadas (X, Y) a jugada en formato UCI."""
        from_square = chess.square(from_coords[0], from_coords[1])
        to_square = chess.square(to_coords[0], to_coords[1])
        return chess.Move(from_square, to_square)

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
        Genera una lista de coordenadas (X, Y) a partir de unas (zx,by) que el imán debe seguir.
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
            print(f"Movimiento directo para {piece}")
            return [origin, target]
        
        # Si hay obstáculos o es un Caballo, usamos la ruta por los bordes
        print(f"Ruta de evasión activada para {piece}")
        
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
    
    def generate_graveyard_gcode(self, origin):
        """
        Genera G-code para mover una pieza capturada al cementerio desde una posición uci origen.
        origin es una tupla (x, y) en coordenadas del tablero.
        """

        target = (self.GRAVEYARD_X, self.GRAVEYARD_Y)
        instructions = []

        # 1. Moverse a la posición de la pieza capturada
        orig_mm_x, orig_mm_y = self.to_real_mm(origin)
        instructions.append(self.format_gcode("G0", orig_mm_x, orig_mm_y))
        instructions.append("M8 ; MAGNET ON")   

        # 2. Ver si hay colisiones en el camino hacia el cementerio
        # NO podemos usar is_path_clear porque no es un movimiento de ajedrez, así que asumimos que siempre hay obstáculos
        # Ruta de evasión: mover a la intersección por las líneas
        waypoint1 = (origin[0] + 0.5, origin[1] + 0.5)
        waypoint2 = (target[0] + 0.5, origin[1] + 0.5)
        waypoint3 = (target[0] + 0.5, target[1] + 0.5)  

        # 3. Generar G-code para cada paso
        for step in [waypoint1, waypoint2, waypoint3, target]:
            step_x, step_y = self.to_real_mm(step)
            instructions.append(self.format_gcode("G1", step_x, step_y))    
        instructions.append("M9 ; MAGNET OFF")  # Apagamos el imán al final

        return instructions

    def process_full_move (self, move):
        """
        Coordina el movimiento completo
        """
        instructions= []
        origin, target = self.translate_to_matrix(move)

        # Excepción 1: Eliminación de pieza (captura)
        if self.get_piece_at(move.to_square) != "EMPTY" :
            # La dirección destino tiene una pieza, hay eliminación
            instructions.append("; --- FASE: RETIRAR PIEZA ---")

            instructions += self.generate_graveyard_gcode(target) 
        
        #Excepción 2: Coronación del peón
        if self.get_piece_at(move.from_square) == "PAWN" and move.to_square in [chess.A8, chess.H8, chess.A1, chess.H1]:
            # El peón ha llegado a la última fila
            instructions.append("; --- FASE: CORONACIÓN ---")
            # Aquí podrías añadir instrucciones específicas para coronar, si tu robot tiene un mecanismo para ello.
            # Por ahora, solo añadimos un comentario.
            instructions.append("; Nota: Coronación detectada. Asegúrate de cambiar la pieza manualmente si es necesario.")


        # 2. Una vez eliminada la pieza, movemos la pieza
        path = self.plan_path(move)
        instructions.append("; ---INICIO MOVIMIENTO PIEZA ---")

        orig_mm_x, orig_mm_y = self.to_real_mm(path[0]) # Punto origen en mm

        instructions.append(self.format_gcode("G0", orig_mm_x, orig_mm_y))
        instructions.append("M8 ; MAGNET ON")

        # Recorremos los puntos intermedios 
        for step in path[1:]:
            step_x, step_y = self.to_real_mm(step)
            instructions.append(self.format_gcode("G1", step_x, step_y))
        
        instructions.append("M9 ; MAGNET OFF")

        return instructions



