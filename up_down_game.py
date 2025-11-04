
import tkinter as tk
from tkinter import messagebox
import requests
import random

class UpDownGame:
    def __init__(self, window):
        self.window = window
        self.window.title("Up-Down Number Guessing Game")
        self.window.geometry("500x300")

        self.fact_label = tk.Label(self.window, text="", wraplength=480, justify="center", font=("Arial", 12))
        self.fact_label.pack(pady=10)

        self.feedback_label = tk.Label(self.window, text="Guess the number replaced by '?'", font=("Arial", 10))
        self.feedback_label.pack(pady=5)

        self.entry = tk.Entry(self.window, font=("Arial", 14))
        self.entry.pack(pady=5)

        self.guess_button = tk.Button(self.window, text="Guess", command=self.check_guess, font=("Arial", 12))
        self.guess_button.pack(pady=5)

        self.restart_button = tk.Button(self.window, text="Restart", command=self.start_game, font=("Arial", 12))
        self.restart_button.pack(pady=10)
        
        self.attempts_label = tk.Label(self.window, text="Attempts: 0", font=("Arial", 10))
        self.attempts_label.pack(pady=5)

        self.start_game()

    def start_game(self):
        """Initializes or restarts the game."""
        self.secret_number = random.randint(1, 1000)
        self.guess_count = 0
        self.attempts_label.config(text="Attempts: 0")
        self.entry.delete(0, tk.END)
        self.guess_button.config(state="normal")
        
        try:
            # Fetch a fact about the number from the Numbers API
            url = f"http://numbersapi.com/{self.secret_number}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()  # Raise an exception for bad status codes
            fact = response.text
            
            # Replace the number in the fact with a question mark
            modified_fact = fact.replace(str(self.secret_number), "?")
            self.fact_label.config(text=modified_fact)
            self.feedback_label.config(text="I've chosen a number between 1 and 1000. Guess it!")

        except requests.exceptions.RequestException as e:
            self.fact_label.config(text="Could not fetch a fun fact. Let's just play!")
            self.feedback_label.config(text=f"Error: {e}")
            messagebox.showerror("API Error", "Failed to connect to the Numbers API. Please check your internet connection.")


    def check_guess(self):
        """Checks the user's guess against the secret number."""
        try:
            guess = int(self.entry.get())
            self.guess_count += 1
            self.attempts_label.config(text=f"Attempts: {self.guess_count}")

            if guess < self.secret_number:
                self.feedback_label.config(text="UP!", fg="blue")
            elif guess > self.secret_number:
                self.feedback_label.config(text="DOWN!", fg="red")
            else:
                self.feedback_label.config(text="CORRECT!", fg="green")
                self.guess_button.config(state="disabled")
                messagebox.showinfo("Congratulations!", f"You guessed the number {self.secret_number} in {self.guess_count} attempts!")

        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid number.")
        finally:
            self.entry.delete(0, tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    game = UpDownGame(root)
    root.mainloop()
