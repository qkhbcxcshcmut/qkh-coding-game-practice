import tkinter as tk
from tkinter import ttk
import random
import time
import pygame

class MemoryGame:
    def __init__(self, root):
        # Initialize pygame mixer for sounds
        pygame.mixer.init()
        
        self.root = root
        self.root.title("Memory Card Game")
        self.root.configure(bg="#e0e7ff")  # Soft indigo background
        self.root.geometry("800x600")  # Fixed window size
        self.root.resizable(False, False)
        self.root.option_add("*Font", "Arial")  # Set default font

        # Game variables
        self.emojis = ['🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼']
        self.cards = []
        self.first_card = None
        self.second_card = None
        self.has_flipped_card = False
        self.lock_board = False
        self.score = 0
        self.moves = 0
        self.seconds = 0
        self.matched_pairs = 0
        self.total_pairs = len(self.emojis)
        self.timer_running = False

        # Load sounds
        try:
            self.flip_sound = pygame.mixer.Sound("flip.wav")
            self.match_sound = pygame.mixer.Sound("match.wav")
            self.no_match_sound = pygame.mixer.Sound("no_match.wav")
            self.win_sound = pygame.mixer.Sound("win.wav")
            # Load and play background music
            pygame.mixer.music.load("background_music.mp3")
            pygame.mixer.music.set_volume(0.3)  # Set volume to 30%
            pygame.mixer.music.play(-1)  # Loop indefinitely
        except pygame.error as e:
            print(f"Error loading sound files: {e}")
            # Continue without sounds if files are missing

        # Style configuration
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 12, "bold"), padding=10)
        self.style.configure("Stats.TLabel", font=("Arial", 12, "bold"), background="#ffffff", padding=8)
        self.style.configure("Header.TLabel", font=("Arial", 24, "bold"), background="#e0e7ff", foreground="#4338ca")
        self.style.map("TButton", background=[("active", "#3b82f6")], foreground=[("active", "white")])

        # Create UI elements
        self.create_ui()
        self.init_game()

    def create_ui(self):
        # Main frame for centering
        self.main_frame = tk.Frame(self.root, bg="#e0e7ff")
        self.main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Header
        self.header = ttk.Label(self.main_frame, text="Memory Card Game\nFind the Pairs", style="Header.TLabel")
        self.header.pack(pady=(0, 20))

        # Stats frame
        self.stats_frame = tk.Frame(self.main_frame, bg="#e0e7ff")
        self.stats_frame.pack(pady=10)

        # Score
        self.score_label = ttk.Label(self.stats_frame, text="Score: 0", style="Stats.TLabel")
        self.score_label.pack(side="left", padx=10)

        # Moves
        self.moves_label = ttk.Label(self.stats_frame, text="Moves: 0", style="Stats.TLabel")
        self.moves_label.pack(side="left", padx=10)

        # Timer
        self.timer_label = ttk.Label(self.stats_frame, text="Time: 00:00", style="Stats.TLabel")
        self.timer_label.pack(side="left", padx=10)

        # Restart button
        self.restart_button = ttk.Button(self.stats_frame, text="Play Again", command=self.init_game, style="TButton")
        self.restart_button.pack(side="left", padx=10)

        # Game board
        self.board_frame = tk.Frame(self.main_frame, bg="#e0e7ff")
        self.board_frame.pack(pady=20)

        # Configure grid weights for proper scaling
        for i in range(4):
            self.board_frame.grid_rowconfigure(i, weight=1)
            self.board_frame.grid_columnconfigure(i, weight=1)

        # Win dialog (initially hidden)
        self.win_dialog = tk.Toplevel(self.root)
        self.win_dialog.withdraw()
        self.win_dialog.transient(self.root)
        self.win_dialog.configure(bg="#ffffff")
        self.win_dialog.geometry("400x300")
        self.win_dialog.resizable(False, False)
        self.win_dialog.protocol("WM_DELETE_WINDOW", lambda: None)

        win_frame = tk.Frame(self.win_dialog, bg="#ffffff")
        win_frame.pack(expand=True, fill="both", padx=20, pady=20)

        tk.Label(win_frame, text="Congratulations!", font=("Arial", 20, "bold"), bg="#ffffff", fg="#16a34a").pack(pady=10)
        self.win_message = tk.Label(win_frame, text="", font=("Arial", 14), bg="#ffffff", justify="center")
        self.win_message.pack(pady=10)
        ttk.Button(win_frame, text="Play Again", command=self.play_again, style="TButton").pack(pady=10)

    def init_game(self):
        # Reset game state
        self.score = 0
        self.moves = 0
        self.seconds = 0
        self.matched_pairs = 0
        self.has_flipped_card = False
        self.lock_board = False
        self.first_card = None
        self.second_card = None
        self.update_stats()
        self.win_dialog.withdraw()

        # Clear existing cards
        for widget in self.board_frame.winfo_children():
            widget.destroy()
        self.cards = []

        # Create card pairs
        game_emojis = self.emojis + self.emojis
        random.shuffle(game_emojis)

        # Create card buttons
        for i, emoji in enumerate(game_emojis):
            row, col = divmod(i, 4)  # 4x4 grid
            card = tk.Button(self.board_frame, text="?", font=("Segoe UI Emoji", 24), bg="#4f46e5", fg="white",
                             width=80, height=80, relief="raised", borderwidth=2, compound="center",
                             command=lambda idx=i: self.flip_card(idx))
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            card.emoji = emoji
            # Hover effect
            card.bind("<Enter>", lambda e, c=card: c.configure(bg="#6b7280") if c["state"] != "disabled" else None)
            card.bind("<Leave>", lambda e, c=card: c.configure(bg="#4f46e5") if c["state"] != "disabled" else None)
            self.cards.append(card)

        # Start timer
        self.timer_running = True
        self.update_timer()

        # Restart background music if stopped
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)

    def flip_card(self, index):
        if self.lock_board or self.cards[index] == self.first_card or self.cards[index]["state"] == "disabled":
            return

        card = self.cards[index]
        card.configure(text=card.emoji, bg="#3b82f6")  # Flip to show emoji

        # Play flip sound
        try:
            self.flip_sound.play()
        except AttributeError:
            pass

        if not self.has_flipped_card:
            # First card
            self.has_flipped_card = True
            self.first_card = card
        else:
            # Second card
            self.second_card = card
            self.moves += 1
            self.update_stats()
            self.check_for_match()

    def check_for_match(self):
        if self.first_card.emoji == self.second_card.emoji:
            # Match
            self.score += 1
            self.matched_pairs += 1
            self.first_card.configure(state="disabled", bg="#3b82f6")
            self.second_card.configure(state="disabled", bg="#3b82f6")
            try:
                self.match_sound.play()
            except AttributeError:
                pass
            self.reset_board()
            self.update_stats()

            if self.matched_pairs == self.total_pairs:
                self.end_game()
        else:
            # No match
            self.lock_board = True
            try:
                self.no_match_sound.play()
            except AttributeError:
                pass
            self.root.after(1000, self.unflip_cards)

    def unflip_cards(self):
        self.first_card.configure(text="?", bg="#4f46e5")
        self.second_card.configure(text="?", bg="#4f46e5")
        self.reset_board()

    def reset_board(self):
        self.has_flipped_card = False
        self.lock_board = False
        self.first_card = None
        self.second_card = None

    def update_stats(self):
        self.score_label.configure(text=f"Score: {self.score}")
        self.moves_label.configure(text=f"Moves: {self.moves}")
        minutes = self.seconds // 60
        seconds = self.seconds % 60
        self.timer_label.configure(text=f"Time: {minutes:02d}:{seconds:02d}")

    def update_timer(self):
        if self.timer_running:
            self.seconds += 1
            self.update_stats()
            self.root.after(1000, self.update_timer)

    def end_game(self):
        self.timer_running = False
        message = f"You completed the game!\nScore: {self.score}\nMoves: {self.moves}\nTime: {self.timer_label.cget('text').split(': ')[1]}"
        self.win_message.configure(text=message)
        self.win_dialog.deiconify()
        self.win_dialog.grab_set()
        # Play win sound
        try:
            pygame.mixer.music.stop()
            self.win_sound.play()
        except AttributeError:
            pass

    def play_again(self):
        self.win_dialog.withdraw()
        self.init_game()

if __name__ == "__main__":
    root = tk.Tk()
    game = MemoryGame(root)
    root.mainloop()