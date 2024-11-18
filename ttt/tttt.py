import tkinter as tk
from tkinter import messagebox
import random
from ai.tttt import get_best_move, check_winner  # Updated import

class TicTacToe:
    def __init__(self, master):
        self.master = master
        self.master.title("Tic-Tac-Toe")
        self.master.geometry("1400x1200")
        self.master.configure(bg='lightgray')
        self.current_player = 'Red'
        self.board = [[' ' for _ in range(4)] for _ in range(4)]  # Keep 4x4 board
        self.buttons = [[None for _ in range(4)] for _ in range(4)]  # Keep 4x4 buttons
        self.game_mode = None
        self.ai_player = 'Green'
        self.human_player = 'Red'
        self.replay_button = None

        print("Initial board state:")
        for row in self.board:
            print(row)

        self.create_start_screen()

    def create_start_screen(self):
        self.start_frame = tk.Frame(self.master, bg='lightgray')
        self.start_frame.pack(expand=True, fill=tk.BOTH, padx=50, pady=50)

        self.pvp_button = tk.Button(self.start_frame, text="Player vs Player", font=('Arial', 56), command=lambda: self.start_game("PvP"), padx=20, pady=20)
        self.pvp_button.pack(expand=True, pady=40)

        self.pve_button = tk.Button(self.start_frame, text="Player vs AI", font=('Arial', 56), command=lambda: self.start_game("PvE"), padx=20, pady=20)
        self.pve_button.pack(expand=True, pady=40)

    def start_game(self, mode):
        self.game_mode = mode
        if hasattr(self, 'start_frame'):
            self.start_frame.destroy()
        
        self.game_frame = tk.Frame(self.master, bg='lightgray')
        self.game_frame.pack(expand=True, fill=tk.BOTH, padx=50, pady=50)
        
        # Create a frame for control buttons
        self.control_frame = tk.Frame(self.master, bg='lightgray')
        self.control_frame.pack(pady=10)
        
        # Create Quit and Restart buttons
        self.quit_button = tk.Button(self.control_frame, text='Quit', font=('Arial', 20), 
                                     command=self.quit_game, bg='red', fg='white')
        self.quit_button.pack(side=tk.LEFT, padx=10)
        
        self.restart_button = tk.Button(self.control_frame, text='Restart', font=('Arial', 20), 
                                        command=self.restart_game, bg='blue', fg='white')
        self.restart_button.pack(side=tk.LEFT, padx=10)
        
        self.status_label = tk.Label(self.master, text="Red's turn", font=('Arial', 64), fg='red', bg='lightgray')
        self.status_label.pack(pady=10)

        # Create a new frame for the game buttons
        self.game_buttons_frame = tk.Frame(self.game_frame, bg='lightgray')
        self.game_buttons_frame.pack(expand=True, fill=tk.BOTH, padx=50, pady=50)

        for i in range(4):
            self.game_buttons_frame.grid_rowconfigure(i, weight=1)
            self.game_buttons_frame.grid_columnconfigure(i, weight=1)

        self.buttons = [[None for _ in range(4)] for _ in range(4)]  # Reset buttons array

        for i in range(4):
            for j in range(4):
                button_frame = tk.Frame(self.game_buttons_frame, bg='white')
                button_frame.grid(row=i, column=j, sticky="nsew", padx=15, pady=15)
                
                self.buttons[i][j] = tk.Button(button_frame, text=' ', font=('Arial', 120, 'bold'),
                                               command=lambda row=i, col=j: self.make_move(row, col),
                                               relief=tk.RAISED, borderwidth=8)
                self.buttons[i][j].place(relx=0, rely=0, relwidth=1, relheight=1)

        if mode == "PvE":
            self.randomly_choose_first_player()
        else:
            self.current_player = self.human_player
        
        self.update_status_label()

        if self.game_mode == "PvE" and self.current_player == self.ai_player:
            self.master.after(500, self.ai_move)

    def make_move(self, row, col):
        if self.board[row][col] == ' ':
            self.board[row][col] = self.current_player
            color = 'red' if self.current_player == 'Red' else 'green'
            
            self.buttons[row][col].config(bg=color, state='disabled')
            
            winner = self.check_winner()
            if winner:
                self.end_game(f"{winner} wins!")
            elif self.is_full():
                self.end_game("It's a tie!")
            else:
                self.current_player = self.ai_player if self.current_player == self.human_player else self.human_player
                self.update_status_label()

                if self.game_mode == "PvE" and self.current_player == self.ai_player:
                    self.master.after(500, self.ai_move)

    def randomly_choose_first_player(self):
        self.current_player = random.choice([self.human_player, self.ai_player])

    def update_status_label(self):
        self.status_label.config(text=f"{self.current_player}'s turn", fg=self.current_player.lower(), font=('Arial', 64))

    def end_game(self, message):
        messagebox.showinfo("Game Over", message)
        self.status_label.config(text="Game Over")

    def quit_game(self):
        # Destroy the game frame, status label, and control frame
        if hasattr(self, 'game_frame'):
            self.game_frame.destroy()
        if hasattr(self, 'status_label'):
            self.status_label.destroy()
        if hasattr(self, 'control_frame'):
            self.control_frame.destroy()
        
        # Reset the game state
        self.board = [[' ' for _ in range(4)] for _ in range(4)]
        self.current_player = 'Red'
        self.game_mode = None
        
        # Recreate the start screen
        self.create_start_screen()

    def check_winner(self):
        # Use the check_winner function from ai/tttt.py
        return check_winner(self.board)

    def is_full(self):
        return all(cell != ' ' for row in self.board for cell in row)

    def ai_move(self):
        print("AI is making a move...")
        print("Current board state:")
        for row in self.board:
            print(row)
        move = get_best_move(self.board)
        if move is None:
            print("Error: AI couldn't find a valid move!")
            return
        row, col = move
        print(f"AI chose move: ({row}, {col})")
        if row < 0 or row > 3 or col < 0 or col > 3:  # Keep 4x4 board check
            print("Error: AI returned an invalid move!")
            return
        if self.board[row][col] != ' ':
            print("Error: AI tried to make a move on an occupied space!")
            return
        self.make_move(row, col)

    def restart_game(self):
        # Destroy the current game frame, status label, and control frame
        if hasattr(self, 'game_frame'):
            self.game_frame.destroy()
        if hasattr(self, 'status_label'):
            self.status_label.destroy()
        if hasattr(self, 'control_frame'):
            self.control_frame.destroy()
        
        # Reset the game state
        self.board = [[' ' for _ in range(4)] for _ in range(4)]  # Keep 4x4 board
        self.current_player = 'Red'
        
        # Start a new game with the same mode
        self.start_game(self.game_mode)

if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()