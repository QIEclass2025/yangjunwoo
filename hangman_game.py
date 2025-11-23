
import tkinter as tk
from tkinter import messagebox
import requests
import random
from PIL import Image, ImageTk
from io import BytesIO

class HangmanGame:
    def __init__(self, root):
        self.root = root
        self.root.title("행맨 게임")
        self.pokemon_name = ""
        self.guesses_left = 8
        self.wrong_guesses = 0
        self.guessed_letters = set()
        self.original_pokemon_image = None
        self.pokemon_image_on_canvas = None
        self.setup_game()

    def setup_game(self):
        self.fetch_random_pokemon()
        self.create_widgets()

    def fetch_random_pokemon(self):
        try:
            random_id = random.randint(1, 151)
            response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{random_id}")
            response.raise_for_status()
            pokemon_data = response.json()
            self.pokemon_name = pokemon_data["name"].replace("-", "").upper()
        except requests.exceptions.RequestException as e:
            self.pokemon_name = "PYTHON" # Fallback
            print(f"API 요청 실패: {e}")

    def create_widgets(self):
        # Configure grid layout
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.image_canvas = tk.Canvas(self.root)
        self.image_canvas.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.image_canvas.bind("<Configure>", self.redraw_pokemon_image)

        self.word_label = tk.Label(self.root, text="", font=("Helvetica", 24))
        self.word_label.grid(row=1, column=0, sticky="ew", padx=10)

        self.guesses_label = tk.Label(self.root, text=f"남은 기회: {self.guesses_left}", font=("Helvetica", 16))
        self.guesses_label.grid(row=2, column=0, sticky="ew", padx=10)

        button_frame = tk.Frame(self.root)
        button_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)

        # Configure button frame grid
        for i in range(7):
            button_frame.grid_columnconfigure(i, weight=1)
        for i in range(4):
            button_frame.grid_rowconfigure(i, weight=1)

        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            button = tk.Button(button_frame, text=letter, command=lambda l=letter: self.guess_letter(l))
            row = (ord(letter) - ord('A')) // 7
            col = (ord(letter) - ord('A')) % 7
            button.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
        
        self.update_word_display()

    def guess_letter(self, letter):
        if letter in self.guessed_letters:
            return

        self.guessed_letters.add(letter)

        if letter in self.pokemon_name:
            self.update_word_display()
        else:
            self.guesses_left -= 1
            self.wrong_guesses += 1
            self.guesses_label.config(text=f"남은 기회: {self.guesses_left}")
            if self.wrong_guesses == 5:
                self.show_pokemon_image()

        # Disable the button
        for child in self.root.winfo_children():
            if isinstance(child, tk.Frame):
                for button in child.winfo_children():
                    if button["text"] == letter:
                        button.config(state=tk.DISABLED)
        
        self.check_game_over()

    def update_word_display(self):
        display_word = " ".join([letter if letter in self.guessed_letters else "_" for letter in self.pokemon_name])
        self.word_label.config(text=display_word)

    def show_pokemon_image(self):
        try:
            response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{self.pokemon_name.lower()}")
            response.raise_for_status()
            pokemon_data = response.json()
            image_url = pokemon_data["sprites"]["front_default"]

            image_response = requests.get(image_url)
            self.original_pokemon_image = Image.open(BytesIO(image_response.content))
            self.redraw_pokemon_image()
        except requests.exceptions.RequestException as e:
            print(f"이미지 로드 실패: {e}")

    def redraw_pokemon_image(self, event=None):
        if not self.original_pokemon_image:
            return

        canvas_width = self.image_canvas.winfo_width()
        canvas_height = self.image_canvas.winfo_height()

        if canvas_width < 2 or canvas_height < 2:
            return

        img_width, img_height = self.original_pokemon_image.size
        if img_width == 0 or img_height == 0:
            return
            
        ratio = min(canvas_width / img_width, canvas_height / img_height)
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)

        if new_width < 1 or new_height < 1:
            return

        resized_image = self.original_pokemon_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.pokemon_image = ImageTk.PhotoImage(resized_image)

        if self.pokemon_image_on_canvas:
            self.image_canvas.delete(self.pokemon_image_on_canvas)
        
        self.pokemon_image_on_canvas = self.image_canvas.create_image(
            canvas_width / 2,
            canvas_height / 2,
            image=self.pokemon_image
        )

    def check_game_over(self):
        if "_" not in self.word_label.cget("text"):
            self.show_win_message()
        elif self.guesses_left == 0:
            self.show_loss_message()

    def show_win_message(self):
        self.word_label.config(text="승리!")
        self.ask_play_again()

    def show_loss_message(self):
        self.word_label.config(text=f"패배! 정답: {self.pokemon_name}")
        self.ask_play_again()

    def ask_play_again(self):
        play_again = tk.messagebox.askyesno("게임 종료", "다시 하시겠습니까?")
        if play_again:
            self.restart_game()
        else:
            self.root.quit()

    def restart_game(self):
        # 기존 위젯 모두 제거
        for widget in self.root.winfo_children():
            widget.destroy()

        # 게임 상태 초기화 및 위젯 재생성
        self.guesses_left = 8
        self.wrong_guesses = 0
        self.guessed_letters = set()
        self.original_pokemon_image = None
        self.pokemon_image_on_canvas = None
        self.setup_game()

if __name__ == "__main__":
    root = tk.Tk()
    game = HangmanGame(root)
    root.mainloop()
