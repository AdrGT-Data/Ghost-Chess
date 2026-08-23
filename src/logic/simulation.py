import turtle
import chess
"""
Script que contiene la clase MagnetSimulator, que se encarga de simular gráficamente el movimiento del imán y la disposición de las piezas en un tablero de ajedrez.
El tablero se dibuja en una ventana de Turtle, y el imán se representa como un punto que se mueve según las instrucciones G-code. Las piezas se representan con letras en las casillas correspondientes, y se puede resaltar la última jugada realizada.
"""
class MagnetSimulator:
    def __init__(self, board_size_mm=400, square_size_mm=50):
        self.screen = turtle.Screen()
        self.screen.title("Ghost Chess - Simulador de Interacciones")
        self.screen.bgcolor("#2b2b2b")
        
        # Ajustamos dimensiones para ver el cementerio
        self.screen.setworldcoordinates(-100, -50, board_size_mm + 50, board_size_mm + 50)
        
        # 1. El Imán (Punto que se mueve)
        self.magnet = turtle.Turtle()
        self.magnet.shape("circle")
        self.magnet.color("red")
        self.magnet.turtlesize(0.8)
        self.magnet.penup()
        self.magnet.speed(4)
        
        # 2. El Dibujante de Piezas (Estampa el texto y se oculta)
        self.piece_drawer = turtle.Turtle()
        self.piece_drawer.hideturtle()
        self.piece_drawer.penup()
        self.piece_drawer.speed(0)

        self.magnet_is_on = False

        self._draw_grid(board_size_mm, square_size_mm)

    def _draw_grid(self, board_size, square_size):
        """Dibuja el tablero de ajedrez en el fondo"""
        drawer = turtle.Turtle()
        drawer.speed(0)
        drawer.hideturtle()
        drawer.color("#555555")
        drawer.penup()

        for x in range(0, board_size + 1, square_size):
            drawer.goto(x, 0)
            drawer.pendown()
            drawer.goto(x, board_size)
            drawer.penup()

        for y in range(0, board_size + 1, square_size):
            drawer.goto(0, y)
            drawer.pendown()
            drawer.goto(board_size, y)
            drawer.penup()

    def draw_pieces(self, board, square_size=50):
        """Lee el tablero lógico y dibuja letras en las casillas"""
        self.piece_drawer.clear() # Limpiamos el estado anterior
        
        # Diccionario para traducir de inglés (python-chess) a iniciales en español
        simbolos = {
            'P': 'P', 'N': 'C', 'B': 'A', 'R': 'T', 'Q': 'D', 'K': 'R', # Blancas
            'p': 'P', 'n': 'C', 'b': 'A', 'r': 'T', 'q': 'D', 'k': 'R'  # Negras
        }
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                col = chess.square_file(square)
                row = chess.square_rank(square)
                
                # Calcular el centro exacto de la casilla
                x = (col * square_size) + (square_size / 2)
                y = (row * square_size) + (square_size / 4) # Ligero ajuste hacia abajo para que la letra quede centrada
                
                self.piece_drawer.goto(x, y)
                
                # Color: Blancas = Blanco | Negras = Cian (para que destaquen sobre fondo oscuro)
                color = "white" if piece.color == chess.WHITE else "cyan"
                self.piece_drawer.color(color)
                
                letra = simbolos[piece.symbol()]
                self.piece_drawer.write(letra, align="center", font=("Arial", 16, "bold"))

    def simulate_gcode(self, gcode_list):
        """Simula los movimientos del imán"""
        # Antes de cada simulación, limpiamos el rastro anterior para no saturar la pantalla
        self.magnet.clear() 
        
        for line in gcode_list:
            clean_line = line.split(';')[0].strip()
            if not clean_line:
                continue

            if clean_line == "M8":
                self.magnet_is_on = True
                self.magnet.color("#00ff00") # Imán encendido (Verde)
                self.magnet.pendown()
                
            elif clean_line == "M9":
                self.magnet_is_on = False
                self.magnet.color("red") # Imán apagado (Rojo)
                self.magnet.penup()
                
            elif clean_line.startswith("G0") or clean_line.startswith("G1"):
                parts = clean_line.split()
                x, y = self.magnet.xcor(), self.magnet.ycor()
                
                for p in parts:
                    if p.startswith('X'):
                        x = float(p[1:])
                    elif p.startswith('Y'):
                        y = float(p[1:])
                
                self.magnet.goto(x, y)