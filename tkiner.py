import numpy as np
import tkinter as tk
import random
import math

# === Game Logic ===
ROW_COUNT = 6
COL_COUNT = 7
WINDOW_LEN = 4
PLAYER = 0 #for turns
AI = 1 #for turns
PLAYER_PIECE = 1
AI_PIECE = 2
EMPTY = 0

def create_board():
    return np.zeros((ROW_COUNT, COL_COUNT))

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col): #check if col not full 
    return board[ROW_COUNT - 1][col] == 0

def get_next_open_row(board, col): #return first empty row in col 
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def winning_move(board, piece):  # Checks for 4 in a row horizontally, vertically, or diagonally
    for c in range(COL_COUNT - 3):
        for r in range(ROW_COUNT):
            if all(board[r][c + i] == piece for i in range(4)):
                return True
    for c in range(COL_COUNT):
        for r in range(ROW_COUNT - 3):
            if all(board[r + i][c] == piece for i in range(4)):
                return True
    for c in range(COL_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return True
    for c in range(COL_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if all(board[r - i][c + i] == piece for i in range(4)):
                return True
    return False
 
def get_valid_location(board): # list of columns that aren’t full.
    return [col for col in range(COL_COUNT) if is_valid_location(board, col)]

def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE
    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2
    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4
    return score

def score_position(board, piece):
    score = 0
    center_array = [int(i) for i in list(board[:, COL_COUNT // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3 #high score for center
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COL_COUNT - 3):
            window = row_array[c:c + WINDOW_LEN]
            score += evaluate_window(window, piece)
    for c in range(COL_COUNT):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r + WINDOW_LEN]
            score += evaluate_window(window, piece)
    for r in range(ROW_COUNT - 3):
        for c in range(COL_COUNT - 3):
            window = [board[r + i][c + i] for i in range(WINDOW_LEN)]
            score += evaluate_window(window, piece)
    for r in range(ROW_COUNT - 3):
        for c in range(COL_COUNT - 3):
            window = [board[r + 3 - i][c + i] for i in range(WINDOW_LEN)]
            score += evaluate_window(window, piece)
    return score

def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_location(board)) == 0

def minMax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_location(board)
    terminal_node = is_terminal_node(board)
    if depth == 0 or terminal_node:
        if terminal_node:
            if winning_move(board, AI_PIECE):
                return (None, 1000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -1000000)
            else:
                return (None, 0)
        else:
            return (None, score_position(board, AI_PIECE))
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minMax(b_copy, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value
    else:
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minMax(b_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

# === Tkinter GUI ===
CELL_SIZE = 80

class Connect4GUI:
    def __init__(self, master,depth):
        self.master = master
        self.depth = depth
        self.master.title("Connect 4")
        self.board = create_board()
        self.canvas = tk.Canvas(master, width=COL_COUNT*CELL_SIZE, height=(ROW_COUNT+1)*CELL_SIZE, bg='blue')
        self.canvas.pack()
        self.reset_button = tk.Button(master, text="Reset Game", command=self.reset_game)
        self.reset_button.pack(pady=10)
        self.canvas.bind("<Button-1>", self.player_click)
        self.turn = random.randint(PLAYER, AI)
        self.draw_board()
        self.status_label = tk.Label(master, text="", font=("Helvetica", 16), fg="red", bg="black")
        self.status_label.pack(pady=10)
        if self.turn == AI:
            self.master.after(500, self.ai_move)

    def draw_board(self):
        self.canvas.delete("all")
        for c in range(COL_COUNT):
            for r in range(ROW_COUNT):
                x0 = c * CELL_SIZE
                y0 = (ROW_COUNT - r) * CELL_SIZE  # Flip row vertically
                x1 = x0 + CELL_SIZE
                y1 = y0 + CELL_SIZE
                color = "white"
                if self.board[r][c] == PLAYER_PIECE:
                    color = "red"
                elif self.board[r][c] == AI_PIECE:
                    color = "yellow"
                self.canvas.create_oval(x0+5, y0+5, x1-5, y1-5, fill=color, outline="black")
        self.master.update()
    
    def reset_game(self):
        self.board = create_board()
        self.turn = random.randint(PLAYER, AI)
        self.draw_board()
        if self.turn == AI:
            self.master.after(500, self.ai_move)


    def player_click(self, event):
        if self.turn != PLAYER:
            return
        col = event.x // CELL_SIZE
        if is_valid_location(self.board, col):
            row = get_next_open_row(self.board, col)
            drop_piece(self.board, row, col, PLAYER_PIECE)
            if winning_move(self.board, PLAYER_PIECE):
                self.draw_board()
                self.status_label.config(text="You win!")
                self.master.after(3000, self.master.destroy) 
                return
            self.turn = AI
            self.draw_board()
            self.master.after(500, self.ai_move)

    def ai_move(self):
        col, _ = minMax(self.board, self.depth, -math.inf, math.inf, True)
        if is_valid_location(self.board, col):
            row = get_next_open_row(self.board, col)
            drop_piece(self.board, row, col, AI_PIECE)
            if winning_move(self.board, AI_PIECE):
                self.draw_board()
                self.status_label.config(text="AI wins!")
                self.master.after(2000, self.master.destroy)                
                return
        self.turn = PLAYER
        self.draw_board()

# === Run App ===

root = tk.Tk()
root.geometry("800x700")
root.title("Choose Difficulty")

welcome_label = tk.Label(root, text="Select Difficulty", font=("Helvetica", 18))
welcome_label.pack(pady=20)
tk.Button(root, text="Easy", font=("Helvetica", 14), width=15,
          command=lambda: start_game(2)).pack(pady=5)
tk.Button(root, text="Medium", font=("Helvetica", 14), width=15,
          command=lambda: start_game(3)).pack(pady=5)
tk.Button(root, text="Hard", font=("Helvetica", 14), width=15,
          command=lambda: start_game(4)).pack(pady=5)

def start_game(depth):
    for widget in root.winfo_children():
        widget.destroy()  # Clear the welcome screen
    Connect4GUI(root, depth)

root.mainloop()