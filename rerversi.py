import tkinter as tk
from tkinter import messagebox
import copy
import math

class OthelloGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Othello Game - Enhanced")
        self.board_size = 8
        self.current_player = 'black'
        self.game_over = False
        self.board = self.create_initial_board()
        self.buttons = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.ai_enabled = True
        self.ai_difficulty = 3  # Default depth for minimax
        self.button_font = ('Arial', 14)
        self.status_font = ('Arial', 14, 'bold')
        self.button_width = 6
        self.button_height = 3
        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(self.main_frame)
        self.scrollbar = tk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollable_frame.bind(
             "<Configure>",
             lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.setup_gui()
        self.update_board()
    
    
        
        # Add menu for game options
        self.menu_bar = tk.Menu(self.master)
        self.game_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.game_menu.add_command(label="New Game", command=self.reset_game)
        self.game_menu.add_separator()
        self.game_menu.add_command(label="Exit", command=self.master.quit)
        self.menu_bar.add_cascade(label="Game", menu=self.game_menu)
        
        # AI options
        self.ai_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.ai_var = tk.BooleanVar(value=True)
        self.ai_menu.add_checkbutton(label="Enable AI", variable=self.ai_var, 
                                    command=self.toggle_ai)
        self.ai_menu.add_command(label="Easy (Depth 2)", command=lambda: self.set_ai_difficulty(2))
        self.ai_menu.add_command(label="Medium (Depth 3)", command=lambda: self.set_ai_difficulty(3))
        self.ai_menu.add_command(label="Hard (Depth 4)", command=lambda: self.set_ai_difficulty(4))
        self.menu_bar.add_cascade(label="AI", menu=self.ai_menu)
        
        self.master.config(menu=self.menu_bar)

    def setup_gui(self):
        # Frame for the board with larger padding
        self.board_frame = tk.Frame(self.scrollable_frame)
        self.board_frame.pack(padx=20, pady=20)
        
        # Create larger buttons for each cell
        for row in range(self.board_size):
            for col in range(self.board_size):
                button = tk.Button(
                    self.board_frame, 
                    width=self.button_width, 
                    height=self.button_height,
                    font=self.button_font,
                    command=lambda r=row, c=col: self.make_move(r, c)
                )
                button.grid(row=row, column=col, padx=3, pady=3)
                self.buttons[row][col] = button
        
        # Status frame with larger font
        self.status_frame = tk.Frame(self.scrollable_frame)
        self.status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.current_player_label = tk.Label(
            self.status_frame, 
            text=f"Current Player: {self.current_player.capitalize()}", 
            font=self.status_font
        )
        self.current_player_label.pack(side=tk.LEFT)
        
        self.score_label = tk.Label(
            self.status_frame, 
            text="Black: 2 - White: 2", 
            font=self.status_font
        )
        self.score_label.pack(side=tk.RIGHT)
        
        # Control frame with larger buttons
        self.control_frame = tk.Frame(self.scrollable_frame)
        self.control_frame.pack(pady=10)
        
        tk.Button(
            self.control_frame, 
            text="New Game", 
            command=self.reset_game,
            font=self.status_font,
            padx=15
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            self.control_frame, 
            text="Pass", 
            command=self.pass_turn,
            font=self.status_font,
            padx=15
        ).pack(side=tk.LEFT, padx=10)

        self.difficulty_frame = tk.Frame(self.scrollable_frame)
        self.difficulty_frame.pack(pady=10)
        tk.Label(
             self.difficulty_frame,
             text="AI Difficulty:",
             font=self.status_font
             ).pack(side=tk.LEFT, padx=5)
        self.difficulty_var = tk.StringVar(value="3")  # Default to Medium
        difficulties = [("Easy", "2"), ("Medium", "3"), ("Hard", "4")]
        for text, level in difficulties:
            tk.Radiobutton(
                 self.difficulty_frame,
                 text=text,
                 variable=self.difficulty_var,
                 value=level,
                 command=lambda l=int(level): self.set_ai_difficulty(l),
                 font=self.button_font
                 ).pack(side=tk.LEFT, padx=5)
    def set_ai_difficulty(self, depth):
        self.ai_difficulty = depth
        status = {
            2: "Easy (Depth 2)",
            3: "Medium (Depth 3)", 
            4: "Hard (Depth 4)"
            }[depth]
        self.current_player_label.config(text=f"AI Level: {status}")

    def create_initial_board(self):
        board = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]
        # Set up the initial pieces
        mid = self.board_size // 2
        board[mid-1][mid-1] = 'white'
        board[mid][mid] = 'white'
        board[mid-1][mid] = 'black'
        board[mid][mid-1] = 'black'
        return board
    
    def reset_game(self):
        self.current_player = 'black'
        self.game_over = False
        self.board = self.create_initial_board()
        self.update_board()
    
    def toggle_ai(self):
        self.ai_enabled = self.ai_var.get()
        if self.ai_enabled and self.current_player == 'white':
            self.ai_move()
    
    def set_ai_difficulty(self, depth):
        self.ai_difficulty = depth
    
    def update_board(self):
        black_count = 0
        white_count = 0
        
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] == 'black':
                    self.buttons[row][col].config(
                        bg='black', 
                        fg='white', 
                        text='●',
                        font=self.button_font
                    )
                    black_count += 1
                elif self.board[row][col] == 'white':
                    self.buttons[row][col].config(
                        bg='white', 
                        fg='black', 
                        text='●',
                        font=self.button_font
                    )
                    white_count += 1
                else:
                    self.buttons[row][col].config(
                        bg='#4CAF50', 
                        text='', 
                        fg='black',
                        font=self.button_font
                    )
        
        self.score_label.config(text=f"Black: {black_count} - White: {white_count}")
        self.current_player_label.config(text=f"Current Player: {self.current_player.capitalize()}")
        
        # Highlight valid moves
        valid_moves = self.get_valid_moves(self.current_player)
        for row, col in valid_moves:
            self.buttons[row][col].config(text='•', font=self.button_font)
        
        # Check if game is over
        if not valid_moves:
            opponent = 'white' if self.current_player == 'black' else 'black'
            if not self.get_valid_moves(opponent):
                self.game_over = True
                winner = self.determine_winner()
                messagebox.showinfo("Game Over", winner)
    
    def make_move(self, row, col):
        if self.game_over or self.board[row][col] is not None:
            return
        
        valid_moves = self.get_valid_moves(self.current_player)
        if (row, col) not in valid_moves:
            return
        
        # Place the piece
        self.board[row][col] = self.current_player
        
        # Flip opponent's pieces
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),          (0, 1),
                      (1, -1),  (1, 0), (1, 1)]
        
        for dr, dc in directions:
            self.flip_pieces(row, col, dr, dc)
        
        # Switch player
        self.switch_player()
        self.update_board()
        
        # AI move if enabled and it's AI's turn
        if self.ai_enabled and self.current_player == 'white' and not self.game_over:
            self.master.after(500, self.ai_move)
    
    def flip_pieces(self, row, col, dr, dc):
        r, c = row + dr, col + dc
        to_flip = []
        
        while 0 <= r < self.board_size and 0 <= c < self.board_size:
            if self.board[r][c] is None:
                break
            elif self.board[r][c] == self.current_player:
                for flip_r, flip_c in to_flip:
                    self.board[flip_r][flip_c] = self.current_player
                break
            else:
                to_flip.append((r, c))
            
            r += dr
            c += dc
    
    def get_valid_moves(self, player):
        valid_moves = []
        
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] is None:
                    if self.is_valid_move(row, col, player):
                        valid_moves.append((row, col))
        
        return valid_moves
    
    def is_valid_move(self, row, col, player):
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),          (0, 1),
                      (1, -1),  (1, 0), (1, 1)]
        
        opponent = 'white' if player == 'black' else 'black'
        
        for dr, dc in directions:
            r, c = row + dr, col + dc
            found_opponent = False
            
            while 0 <= r < self.board_size and 0 <= c < self.board_size:
                if self.board[r][c] is None:
                    break
                elif self.board[r][c] == opponent:
                    found_opponent = True
                elif self.board[r][c] == player and found_opponent:
                    return True
                else:
                    break
                
                r += dr
                c += dc
        
        return False
    
    def switch_player(self):
        self.current_player = 'white' if self.current_player == 'black' else 'black'
        
        # If no valid moves for current player, switch again
        if not self.get_valid_moves(self.current_player):
            self.current_player = 'white' if self.current_player == 'black' else 'black'
    
    def pass_turn(self):
        if not self.get_valid_moves(self.current_player):
            self.switch_player()
            self.update_board()
            
            # AI move if enabled and it's AI's turn
            if self.ai_enabled and self.current_player == 'white' and not self.game_over:
                self.master.after(500, self.ai_move)
    
    def determine_winner(self):
        black_count = sum(row.count('black') for row in self.board)
        white_count = sum(row.count('white') for row in self.board)
        
        if black_count > white_count:
            return f"Black wins! {black_count} - {white_count}"
        elif white_count > black_count:
            return f"White wins! {white_count} - {black_count}"
        else:
            return f"It's a tie! {black_count} - {white_count}"
    
    def ai_move(self):
        if self.current_player != 'white' or self.game_over:
            return
        
        best_move = self.find_best_move()
        if best_move:
            self.make_move(*best_move)
        else:
            self.pass_turn()
    
    def find_best_move(self):
        valid_moves = self.get_valid_moves('white')
        if not valid_moves:
            return None
        
        best_score = -math.inf
        best_move = None
        
        for move in valid_moves:
            board_copy = copy.deepcopy(self.board)
            self.simulate_move(board_copy, move, 'white')
            score = self.minimax(board_copy, self.ai_difficulty, -math.inf, math.inf, False)
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move
    
    def minimax(self, board, depth, alpha, beta, maximizing_player):
        if depth == 0:
            return self.evaluate_board(board)
        
        current_player = 'white' if maximizing_player else 'black'
        valid_moves = self.get_valid_moves_for_board(board, current_player)
        
        if not valid_moves:
            # If no moves available, check if game is over
            opponent = 'black' if maximizing_player else 'white'
            if not self.get_valid_moves_for_board(board, opponent):
                return self.evaluate_board(board)
            
            # Otherwise, pass turn
            return self.minimax(board, depth - 1, alpha, beta, not maximizing_player)
        
        if maximizing_player:
            max_eval = -math.inf
            for move in valid_moves:
                board_copy = copy.deepcopy(board)
                self.simulate_move(board_copy, move, 'white')
                eval = self.minimax(board_copy, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = math.inf
            for move in valid_moves:
                board_copy = copy.deepcopy(board)
                self.simulate_move(board_copy, move, 'black')
                eval = self.minimax(board_copy, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval
    
    def simulate_move(self, board, move, player):
        row, col = move
        board[row][col] = player
        
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),          (0, 1),
                      (1, -1),  (1, 0), (1, 1)]
        
        for dr, dc in directions:
            r, c = row + dr, col + dc
            to_flip = []
            
            while 0 <= r < len(board) and 0 <= c < len(board[0]):
                if board[r][c] is None:
                    break
                elif board[r][c] != player:
                    to_flip.append((r, c))
                elif to_flip:
                    for flip_r, flip_c in to_flip:
                        board[flip_r][flip_c] = player
                    break
                else:
                    break
                
                r += dr
                c += dc
    
    def get_valid_moves_for_board(self, board, player):
        valid_moves = []
        
        for row in range(len(board)):
            for col in range(len(board[0])):
                if board[row][col] is None:
                    if self.is_valid_move_for_board(board, row, col, player):
                        valid_moves.append((row, col))
        
        return valid_moves
    
    def is_valid_move_for_board(self, board, row, col, player):
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),          (0, 1),
                      (1, -1),  (1, 0), (1, 1)]
        
        opponent = 'white' if player == 'black' else 'black'
        
        for dr, dc in directions:
            r, c = row + dr, col + dc
            found_opponent = False
            
            while 0 <= r < len(board) and 0 <= c < len(board[0]):
                if board[r][c] is None:
                    break
                elif board[r][c] == opponent:
                    found_opponent = True
                elif board[r][c] == player and found_opponent:
                    return True
                else:
                    break
                
                r += dr
                c += dc
        
        return False
    
    def evaluate_board(self, board):
        # Simple evaluation function - counts pieces with weights for corners and edges
        white_score = 0
        black_score = 0
        
        # Piece count
        white_count = sum(row.count('white') for row in board)
        black_count = sum(row.count('black') for row in board)
        
        # Corner control (very valuable)
        corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
        for r, c in corners:
            if board[r][c] == 'white':
                white_score += 20
            elif board[r][c] == 'black':
                black_score += 20
        
        # Edge control (valuable)
        edges = []
        for i in range(1, 7):
            edges.extend([(0, i), (7, i), (i, 0), (i, 7)])
        
        for r, c in edges:
            if board[r][c] == 'white':
                white_score += 2
            elif board[r][c] == 'black':
                black_score += 2
        
        # Mobility (number of valid moves)
        white_moves = len(self.get_valid_moves_for_board(board, 'white'))
        black_moves = len(self.get_valid_moves_for_board(board, 'black'))
        white_score += white_moves * 1.5
        black_score += black_moves * 1.5
        
        # Final score
        score = (white_count + white_score) - (black_count + black_score)
        return score

if __name__ == "__main__":
    root = tk.Tk()
    game = OthelloGame(root)
    root.mainloop()