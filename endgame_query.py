import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os

class Piece:
    def __init__(self, type, color, revealed=False):
        self.type = type
        self.color = color
        self.revealed = revealed
        self.position = [-1, -1]
    
    def __str__(self):
        return self.type if self.revealed else "?"

class Board:
    def __init__(self, pos=[]):
        self.squares = [[None for i in range(8)] for j in range(4)]
        for (x, y, tp, color) in pos:
            self.squares[x][y] = Piece(tp, color, revealed=True)
    
    def get_pool(self):
        type_pool = ['K'] + ['G', 'M', 'R', 'N', 'C'] * 2 + ['P'] * 5
        pool = [Piece(tp, 0) for tp in type_pool] + [Piece(tp, 1) for tp in type_pool]
        return pool
    
    def pos_empty(self, pos):
        return self.squares[pos[0]][pos[1]] is None
    
    def count_line(self, pos_a, pos_b):
        if pos_a[0] == pos_b[0]:
            l = min(pos_a[1], pos_b[1])
            r = max(pos_a[1], pos_b[1])
            return sum((1 - self.pos_empty([pos_a[0], x])) for x in range(l, r + 1))
        elif pos_a[1] == pos_b[1]:
            l = min(pos_a[0], pos_b[0])
            r = max(pos_a[0], pos_b[0])
            return sum((1 - self.pos_empty([x, pos_a[1]])) for x in range(l, r + 1))
        else:
            return -1
    
    def eatable(self, pos_a, pos_b):
        A = self.squares[pos_a[0]][pos_a[1]]
        B = self.squares[pos_b[0]][pos_b[1]]
        if A.color == B.color or not A.revealed or not B.revealed:
            return False
        if A.type == 'C':
            cnt = self.count_line(pos_a, pos_b)
            return cnt == 3
        if abs(pos_a[0] - pos_b[0]) + abs(pos_a[1] - pos_b[1]) != 1:
            return False
        if A.type == 'K':
            return B.type != 'P'
        elif A.type == 'P':
            return B.type == 'K' or B.type == 'P'
        else:
            partial_order = {'K': 6, 'G': 5, 'M': 4, 'R': 3, 'N': 2, 'C': 1, 'P': 0}
            return partial_order[A.type] >= partial_order[B.type]

class ChessEndgameUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chinese Chess Endgame Table Checker")
        self.root.geometry("750x800")
        
        # Board setup
        self.board = Board()
        self.current_turn = tk.IntVar(value=0)  # 0 = Red, 1 = Black
        
        # UI state
        self.dragging = False
        self.drag_piece = None
        self.drag_start_pos = None
        
        # Colors and symbols for pieces
        self.piece_colors = {0: "red", 1: "blue"}  # Red player, Black player
        self.piece_symbols = {
            'K': '帥/將', 'G': '士', 'M': '相/象', 'R': '車', 
            'N': '馬', 'C': '炮', 'P': '兵/卒'
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Board frame
        board_frame = ttk.LabelFrame(main_frame, text="Chess Board (4x8)", padding="10")
        board_frame.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Create board squares
        self.squares = []
        for row in range(4):
            square_row = []
            for col in range(8):
                square = tk.Canvas(board_frame, width=60, height=60, 
                                 bg="wheat", highlightthickness=1, highlightbackground="black")
                square.grid(row=row, column=col, padx=1, pady=1)
                square.bind("<Button-1>", lambda e, r=row, c=col: self.on_square_click(e, r, c))
                square.bind("<B1-Motion>", lambda e, r=row, c=col: self.on_drag(e, r, c))
                square.bind("<ButtonRelease-1>", lambda e, r=row, c=col: self.on_drop(e, r, c))
                square_row.append(square)
            self.squares.append(square_row)
        
        # Piece pool frame
        pool_frame = ttk.LabelFrame(main_frame, text="Piece Pool", padding="10")
        pool_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Red pieces
        red_frame = ttk.LabelFrame(pool_frame, text="Red Player", padding="5")
        red_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.red_pieces = []
        red_types = ['K'] + ['G', 'M', 'R', 'N', 'C'] * 2 + ['P'] * 5
        for i, piece_type in enumerate(red_types):
            piece_canvas = tk.Canvas(red_frame, width=40, height=40, bg="lightcoral")
            piece_canvas.grid(row=i//6, column=i%6, padx=2, pady=2)
            piece_canvas.create_text(20, 20, text=piece_type, font=("Arial", 12, "bold"))
            piece_canvas.bind("<Button-1>", lambda e, pt=piece_type: self.on_pool_click(e, pt, 0))
            self.red_pieces.append(piece_canvas)
        
        # Black pieces
        black_frame = ttk.LabelFrame(pool_frame, text="Black Player", padding="5")
        black_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        self.black_pieces = []
        black_types = ['K'] + ['G', 'M', 'R', 'N', 'C'] * 2 + ['P'] * 5
        for i, piece_type in enumerate(black_types):
            piece_canvas = tk.Canvas(black_frame, width=40, height=40, bg="lightblue")
            piece_canvas.grid(row=i//6, column=i%6, padx=2, pady=2)
            piece_canvas.create_text(20, 20, text=piece_type, font=("Arial", 12, "bold"))
            piece_canvas.bind("<Button-1>", lambda e, pt=piece_type: self.on_pool_click(e, pt, 1))
            self.black_pieces.append(piece_canvas)
        
        # Control frame
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Turn selection
        turn_frame = ttk.LabelFrame(control_frame, text="Current Turn", padding="5")
        turn_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Radiobutton(turn_frame, text="Red Player", variable=self.current_turn, 
                       value=0).grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(turn_frame, text="Black Player", variable=self.current_turn, 
                       value=1).grid(row=1, column=0, sticky=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(button_frame, text="Clear Board", 
                  command=self.clear_board).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="Submit Query", 
                  command=self.submit_query).grid(row=0, column=1)
        
        # Result display
        result_frame = ttk.LabelFrame(control_frame, text="Query Result", padding="5")
        result_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        self.result_label = ttk.Label(result_frame, text="No query submitted yet", 
                                     font=("Arial", 12, "bold"))
        self.result_label.grid(row=0, column=0)
        
        # Instructions
        inst_frame = ttk.LabelFrame(control_frame, text="Instructions", padding="5")
        inst_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        instructions = """1. Click pieces from the pool to place them on board
2. Drag pieces on board to move them
3. Right-click pieces to remove them
4. Select current player's turn
5. Click Submit to query endgame result
6. Each arrow's color indicates the outcome of each move 
    (green: win, yellow: draw, red: lose)"""
        
        ttk.Label(inst_frame, text=instructions, justify=tk.LEFT).grid(row=0, column=0)
        
        # Bind right-click for removal
        self.root.bind("<Button-3>", self.on_right_click)
        
        self.update_board_display()
    
    def on_pool_click(self, event, piece_type, color):
        """Handle clicking on piece pool to add pieces to board"""
        self.selected_piece_type = piece_type
        self.selected_piece_color = color
        self.root.configure(cursor="hand2")
        
        # Bind next click to place piece
        self.root.bind("<Button-1>", self.place_piece_from_pool)
    
    def place_piece_from_pool(self, event):
        """Place selected piece from pool onto board"""
        # Find which square was clicked
        for row in range(4):
            for col in range(8):
                square = self.squares[row][col]
                x, y = square.winfo_rootx(), square.winfo_rooty()
                w, h = square.winfo_width(), square.winfo_height()
                
                if (x <= event.x_root <= x + w and y <= event.y_root <= y + h):
                    # Place piece if square is empty
                    if self.board.squares[row][col] is None:
                        piece = Piece(self.selected_piece_type, self.selected_piece_color, revealed=True)
                        piece.position = [row, col]
                        self.board.squares[row][col] = piece
                        self.update_board_display()
                    
                    # Reset cursor and unbind
                    self.root.configure(cursor="")
                    self.root.unbind("<Button-1>")
                    return
        
        # If clicked outside board, cancel
        self.root.configure(cursor="")
        self.root.unbind("<Button-1>")
    
    def on_square_click(self, event, row, col):
        """Handle clicking on board squares"""
        if self.board.squares[row][col] is not None:
            self.dragging = True
            self.drag_piece = self.board.squares[row][col]
            self.drag_start_pos = [row, col]
    
    def on_drag(self, event, row, col):
        """Handle dragging pieces"""
        if self.dragging and self.drag_piece:
            # Visual feedback could be added here
            pass
    
    def on_drop(self, event, row, col):
        """Handle dropping pieces"""
        if self.dragging and self.drag_piece:
            # Find target square
            target_row, target_col = None, None
            for r in range(4):
                for c in range(8):
                    square = self.squares[r][c]
                    x, y = square.winfo_rootx(), square.winfo_rooty()
                    w, h = square.winfo_width(), square.winfo_height()
                    
                    if (x <= event.x_root <= x + w and y <= event.y_root <= y + h):
                        target_row, target_col = r, c
                        break
                if target_row is not None:
                    break
            
            # Move piece if target is valid and empty
            if (target_row is not None and target_col is not None and
                self.board.squares[target_row][target_col] is None):
                
                # Remove from old position
                self.board.squares[self.drag_start_pos[0]][self.drag_start_pos[1]] = None
                
                # Place in new position
                self.drag_piece.position = [target_row, target_col]
                self.board.squares[target_row][target_col] = self.drag_piece
                
                self.update_board_display()
            
            # Reset drag state
            self.dragging = False
            self.drag_piece = None
            self.drag_start_pos = None
    
    def on_right_click(self, event):
        """Handle right-click to remove pieces"""
        for row in range(4):
            for col in range(8):
                square = self.squares[row][col]
                x, y = square.winfo_rootx(), square.winfo_rooty()
                w, h = square.winfo_width(), square.winfo_height()
                
                if (x <= event.x_root <= x + w and y <= event.y_root <= y + h):
                    if self.board.squares[row][col] is not None:
                        self.board.squares[row][col] = None
                        self.update_board_display()
                    return
    
    def update_board_display(self):
        """Update the visual display of the board"""
        for row in range(4):
            for col in range(8):
                square = self.squares[row][col]
                
                items = square.find_all()
                for item in items:
                    tags = square.gettags(item)
                    if 'arrow' not in tags:
                        square.delete(item)
                
                # Draw board pattern
                if (row + col) % 2 == 0:
                    square.configure(bg="wheat")
                else:
                    square.configure(bg="tan")
                
                # Draw piece if present
                piece = self.board.squares[row][col]
                if piece is not None:
                    color = "red" if piece.color == 0 else "blue"
                    # Draw circle background
                    square.create_oval(10, 10, 50, 50, fill="white", outline=color, width=2)
                    # Draw piece text
                    square.create_text(30, 30, text=piece.type, font=("Arial", 14, "bold"), fill=color)
    
    def clear_board(self):
        """Clear all pieces from the board"""
        for row in range(4):
            for col in range(8):
                self.board.squares[row][col] = None
        for row in range(4):
            for col in range(8):
                square = self.squares[row][col]
                # Remove existing arrows (keep pieces)
                items = square.find_all()
                for item in items:
                    tags = square.gettags(item)
                    if 'arrow' in tags:
                        square.delete(item)
        self.update_board_display()
        self.result_label.config(text="Board cleared")
    
    def generate_query_string(self):
        """Generate query string for endgame executable"""
        pieces_info = []
        
        for row in range(4):
            for col in range(8):
                piece = self.board.squares[row][col]
                if piece is not None:
                    # Format: {type}{color}{row}{col}
                    piece_str = f"{piece.type}{piece.color}{row}{col}"
                    pieces_info.append(piece_str)
        
        if not pieces_info:
            return None
        
        pieces_string = "".join(pieces_info)
        turn = self.current_turn.get()
        
        return f"{pieces_string} {turn}"
    
    def parse_endgame_output(self, output_lines):
        """Parse the extended endgame output"""
        if len(output_lines) < 2:
            return None, []
        
        try:
            result = int(output_lines[0])
            neighbor_count = int(output_lines[1])
            
            moves = []
            for i in range(2, 2 + neighbor_count):
                if i < len(output_lines):
                    parts = output_lines[i].split()
                    if len(parts) >= 5:
                        sx, sy, tx, ty, move_result = map(int, parts[:5])
                        moves.append((sx, sy, tx, ty, move_result))
            
            return result, moves
        except (ValueError, IndexError):
            return None, []
        
    def draw_move_arrows(self, moves):
        """Draw colored arrows for each possible move"""
        # Clear existing arrows
        for row in range(4):
            for col in range(8):
                square = self.squares[row][col]
                # Remove existing arrows (keep pieces)
                items = square.find_all()
                for item in items:
                    tags = square.gettags(item)
                    if 'arrow' in tags:
                        square.delete(item)
        
        # Draw new arrows
        for sx, sy, tx, ty, move_result in moves:
            if 0 <= sx < 4 and 0 <= sy < 8 and 0 <= tx < 4 and 0 <= ty < 8:
                source_square = self.squares[sx][sy]
                
                # Calculate the direction vector
                dx = tx - sx  # row difference
                dy = ty - sy  # column difference
                
                # Choose arrow color based on result
                arrow_color = {-1: "green", 0: "yellow", 1: "red"}.get(move_result, "black")
                
                # Draw arrow from center pointing in the direction of movement
                center_x, center_y = 30, 30
                
                # Scale the direction vector for visibility
                arrow_length = 30
                end_x = center_x + dy * arrow_length  # dy affects x-coordinate on screen
                end_y = center_y + dx * arrow_length  # dx affects y-coordinate on screen
                
                # Draw arrow on source square
                source_square.create_line(
                    center_x, center_y, end_x, end_y,
                    fill=arrow_color, width=3, arrow=tk.LAST, 
                    arrowshape=(8, 10, 3), tags="arrow"
                )
    
    def submit_query(self):
        """Submit query to endgame executable"""
        query_string = self.generate_query_string()
        
        if query_string is None:
            self.result_label.config(text="No pieces on board!")
            return
        
        try:
            # Show query being executed
            self.result_label.config(text="Querying endgame table...")
            self.root.update()
            
            # Execute endgame query
            cmd = f"./endgame_build/endgame {query_string}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=200)
            
            if result.returncode == 0:
                output_lines = result.stdout.strip().split('\n')
                main_result, moves = self.parse_endgame_output(output_lines)
                
                if main_result is not None:
                    result_text = {
                        1: "WIN for current player",
                        0: "DRAW",
                        -1: "LOSE for current player"
                    }.get(main_result, f"Unknown result: {main_result}")
                    
                    self.result_label.config(text=f"{result_text} ({len(moves)} moves)")
                    self.draw_move_arrows(moves)
                else:
                    self.result_label.config(text="Failed to parse output")
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                self.result_label.config(text=f"Error: {error_msg}")
                
        except subprocess.TimeoutExpired:
            self.result_label.config(text="Query timed out")
        except FileNotFoundError:
            self.result_label.config(text="Error: ./endgame executable not found")
        except Exception as e:
            self.result_label.config(text=f"Error: {str(e)}")
    
    def add_preset_examples(self):
        """Add some preset example buttons"""
        preset_frame = ttk.LabelFrame(self.root, text="Preset Examples", padding="10")
        preset_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        def load_2v2_example():
            self.clear_board()
            # Example 2v2 position
            self.board.squares[0][0] = Piece('K', 0, revealed=True)
            self.board.squares[0][1] = Piece('P', 0, revealed=True)
            self.board.squares[3][6] = Piece('K', 1, revealed=True)
            self.board.squares[3][7] = Piece('P', 1, revealed=True)
            self.update_board_display()
        
        def load_kgmp_example():
            self.clear_board()
            # Example KGmP position from the slides
            self.board.squares[0][0] = Piece('K', 0, revealed=True)
            self.board.squares[1][1] = Piece('G', 0, revealed=True)
            self.board.squares[2][2] = Piece('M', 1, revealed=True)
            self.board.squares[3][3] = Piece('P', 1, revealed=True)
            self.update_board_display()
        
        ttk.Button(preset_frame, text="Load 2v2 Example", 
                  command=load_2v2_example).grid(row=0, column=0, padx=5)
        ttk.Button(preset_frame, text="Load KGmP Example", 
                  command=load_kgmp_example).grid(row=0, column=1, padx=5)

def main():
    root = tk.Tk()
    app = ChessEndgameUI(root)
    
    # Configure grid weights for resizing
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    
    # Add preset examples
    app.add_preset_examples()
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    main()