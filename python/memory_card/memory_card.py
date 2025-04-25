import tkinter as tk
from tkinter import ttk
import random
import pygame

class MemoryGame:
    def __init__(self, root):
        print("Initializing MemoryGame")
        pygame.mixer.init()
        
        self.root = root
        self.root.title("Memory Card Game")
        self.root.configure(bg="#e0e7ff")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        self.root.option_add("*Font", "Arial")
        
        self.root.protocol("WM_DELETE_WINDOW", self.cleanup)
        
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
        self.timer_id = None
        self.high_score = self.load_high_score()
        
        self.flip_sound = None
        self.match_sound = None
        self.no_match_sound = None
        self.win_sound = None
        try:
            self.flip_sound = pygame.mixer.Sound("flip.wav")
            self.match_sound = pygame.mixer.Sound("match.wav")
            self.no_match_sound = pygame.mixer.Sound("no_match.wav")
            self.win_sound = pygame.mixer.Sound("win.wav")
            pygame.mixer.music.load("background_music.mp3")
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)
        except pygame.error as e:
            print(f"Error loading sound files: {e}")
        
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 12, "bold"), padding=10)
        self.style.configure("Stats.TLabel", font=("Arial", 12, "bold"), background="#ffffff", padding=8)
        self.style.configure("Header.TLabel", font=("Arial", 24, "bold"), background="#e0e7ff", foreground="#4338ca")
        self.style.map("TButton", background=[("active", "#3b82f6")], foreground=[("active", "white")])
        
        self.create_ui()
        self.init_game()
    
    def load_high_score(self):
        """Load the high score from a file."""
        print("Loading high score")
        try:
            with open("highscore.txt", "r") as file:
                score = int(file.read().strip())
                print(f"High score loaded: {score}")
                return score
        except (FileNotFoundError, ValueError):
            print("No high score file found or invalid data, starting with 0")
            return 0
    
    def save_high_score(self):
        """Save the high score to a file."""
        print(f"Saving high score: {self.high_score}")
        try:
            with open("highscore.txt", "w") as file:
                file.write(str(self.high_score))
        except IOError:
            print("Error saving high score")
    
    def create_ui(self):
        print("Creating UI")
        self.main_frame = tk.Frame(self.root, bg="#e0e7ff")
        self.main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        self.header = ttk.Label(self.main_frame, text="Memory Card Game\nFind the Pairs", style="Header.TLabel")
        self.header.pack(pady=(0, 20))
        
        self.stats_frame = tk.Frame(self.main_frame, bg="#e0e7ff")
        self.stats_frame.pack(pady=10)
        
        self.score_label = ttk.Label(self.stats_frame, text="Score: 0", style="Stats.TLabel")
        self.score_label.pack(side="left", padx=10)
        
        self.high_score_label = ttk.Label(self.stats_frame, text=f"High Score: {self.high_score}", style="Stats.TLabel")
        self.high_score_label.pack(side="left", padx=10)
        
        self.moves_label = ttk.Label(self.stats_frame, text="Moves: 0", style="Stats.TLabel")
        self.moves_label.pack(side="left", padx=10)
        
        self.timer_label = ttk.Label(self.stats_frame, text="Time: 00:00", style="Stats.TLabel")
        self.timer_label.pack(side="left", padx=10)
        
        self.restart_button = ttk.Button(self.stats_frame, text="Play Again", command=self.init_game, style="TButton")
        self.restart_button.pack(side="left", padx=10)
        
        self.board_frame = tk.Frame(self.main_frame, bg="#e0e7ff")
        self.board_frame.pack(pady=20)
        
        for i in range(4):
            self.board_frame.grid_rowconfigure(i, weight=1)
            self.board_frame.grid_columnconfigure(i, weight=1)
    
    def create_win_dialog(self):
        print("Creating win dialog")
        if hasattr(self, 'win_dialog'):
            try:
                self.win_dialog.destroy()
            except tk.TclError:
                print("Error destroying previous win dialog")
        
        self.win_dialog = tk.Toplevel(self.root)
        self.win_dialog.transient(self.root)
        self.win_dialog.configure(bg="#ffffff")
        self.win_dialog.geometry("400x300")
        self.win_dialog.resizable(False, False)
        self.win_dialog.protocol("WM_DELETE_WINDOW", self.play_again)
        
        win_frame = tk.Frame(self.win_dialog, bg="#ffffff")
        win_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        tk.Label(win_frame, text="Congratulations!", font=("Arial", 20, "bold"), bg="#ffffff", fg="#16a34a").pack(pady=10)
        self.win_message = tk.Label(win_frame, text="", font=("Arial", 14), bg="#ffffff", justify="center")
        self.win_message.pack(pady=10)
        ttk.Button(win_frame, text="Play Again", command=self.play_again, style="TButton").pack(pady=10)
        
        self.win_dialog.withdraw()
    
    def init_game(self):
        print("Initializing game")
        self.score = 0
        self.moves = 0
        self.seconds = 0
        self.matched_pairs = 0
        self.has_flipped_card = False
        self.lock_board = False
        self.first_card = None
        self.second_card = None
        
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.timer_running = False
        
        for widget in self.board_frame.winfo_children():
            widget.destroy()
        self.cards = []
        
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.play(-1)
        except pygame.error:
            print("Error restarting background music")
        
        game_emojis = self.emojis + self.emojis
        random.shuffle(game_emojis)
        
        for i, emoji in enumerate(game_emojis):
            row, col = divmod(i, 4)
            card = tk.Button(self.board_frame, text="?", font=("Segoe UI Emoji", 24), bg="#4f46e5", fg="white",
                             width=10, height=5, relief="raised", borderwidth=2, compound="center",
                             command=lambda idx=i: self.flip_card(idx))
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            card.emoji = emoji
            card.bind("<Enter>", lambda e, c=card: c.configure(bg="#6b7280") if c["state"] != "disabled" else None)
            card.bind("<Leave>", lambda e, c=card: c.configure(bg="#4f46e5") if c["state"] != "disabled" else None)
            self.cards.append(card)
        
        self.create_win_dialog()
        self.update_stats()
        self.timer_running = True
        self.update_timer()
    
    def flip_card(self, index):
        print(f"Flipping card {index}")
        if self.lock_board or self.cards[index] == self.first_card or self.cards[index]["state"] == "disabled":
            return
        
        card = self.cards[index]
        card.configure(text=card.emoji, bg="#3b82f6")
        
        if self.flip_sound:
            try:
                self.flip_sound.play()
            except pygame.error:
                print("Error playing flip sound")
        
        if not self.has_flipped_card:
            self.has_flipped_card = True
            self.first_card = card
        else:
            self.second_card = card
            self.moves += 1
            self.update_stats()
            self.check_for_match()
    
    def check_for_match(self):
        print("Checking for match")
        if self.first_card.emoji == self.second_card.emoji:
            self.score += 100
            print(f"Match found! Score increased by 100 to {self.score}")
            self.matched_pairs += 1
            self.first_card.configure(state="disabled", bg="#3b82f6")
            self.second_card.configure(state="disabled", bg="#3b82f6")
            if self.match_sound:
                try:
                    self.match_sound.play()
                except pygame.error:
                    print("Error playing match sound")
            self.reset_board()
            self.update_stats()
            
            if self.matched_pairs == self.total_pairs:
                self.end_game()
        else:
            self.score = max(0, self.score - 10)
            print(f"No match. Score decreased by 10 to {self.score}")
            self.lock_board = True
            if self.no_match_sound:
                try:
                    self.no_match_sound.play()
                except pygame.error:
                    print("Error playing no_match sound")
            self.root.after(1000, self.unflip_cards)
    
    def unflip_cards(self):
        print("Unflipping cards")
        self.first_card.configure(text="?", bg="#4f46e5")
        self.second_card.configure(text="?", bg="#4f46e5")
        self.reset_board()
    
    def reset_board(self):
        print("Resetting board")
        self.has_flipped_card = False
        self.lock_board = False
        self.first_card = None
        self.second_card = None
    
    def update_stats(self):
        self.score_label.configure(text=f"Score: {self.score}")
        self.high_score_label.configure(text=f"High Score: {self.high_score}")
        self.moves_label.configure(text=f"Moves: {self.moves}")
        minutes = self.seconds // 60
        seconds = self.seconds % 60
        self.timer_label.configure(text=f"Time: {minutes:02d}:{seconds:02d}")
    
    def update_timer(self):
        if self.timer_running:
            self.seconds += 1
            self.update_stats()
            self.timer_id = self.root.after(1000, self.update_timer)
    
    def end_game(self):
        print("Ending game")
        self.timer_running = False
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        
        # Update high score if current score is higher
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
            print(f"New high score: {self.high_score}")
        
        try:
            pygame.mixer.music.stop()
            if self.win_sound:
                self.win_sound.play()
        except pygame.error:
            print("Error handling audio in end_game")
        
        message = f"You completed the game!\nScore: {self.score}\nHigh Score: {self.high_score}\nMoves: {self.moves}\nTime: {self.timer_label.cget('text').split(': ')[1]}"
        try:
            self.win_message.configure(text=message)
            self.win_dialog.deiconify()
            print("Win dialog shown")
        except tk.TclError:
            print("Error showing win dialog")
    
    def play_again(self):
        print("Play again triggered")
        try:
            self.win_dialog.withdraw()
            self.win_dialog.destroy()
        except tk.TclError:
            print("Error destroying win dialog in play_again")
        self.init_game()
    
    def cleanup(self):
        print("Cleaning up")
        self.timer_running = False
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        try:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except pygame.error:
            print("Error cleaning up pygame")
        try:
            if hasattr(self, 'win_dialog'):
                self.win_dialog.destroy()
        except tk.TclError:
            print("Error destroying win dialog in cleanup")
        self.root.destroy()

if __name__ == "__main__":
    print("Starting main loop")
    root = tk.Tk()
    game = MemoryGame(root)
    root.mainloop()