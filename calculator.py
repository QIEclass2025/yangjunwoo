import tkinter as tk

class Calculator:
    def __init__(self, master):
        self.master = master
        master.title("계산기")

        self.display = tk.Entry(master, width=20, font=("Arial", 20), borderwidth=5, justify="right")
        self.display.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

        self.create_button("7", 1, 0)
        self.create_button("8", 1, 1)
        self.create_button("9", 1, 2)
        self.create_button("/", 1, 3)

        self.create_button("4", 2, 0)
        self.create_button("5", 2, 1)
        self.create_button("6", 2, 2)
        self.create_button("*", 2, 3)

        self.create_button("1", 3, 0)
        self.create_button("2", 3, 1)
        self.create_button("3", 3, 2)
        self.create_button("-", 3, 3)

        self.create_button("0", 4, 0)
        self.create_button(".", 4, 1)
        self.create_button("C", 4, 2)
        self.create_button("+", 4, 3)

        self.create_button("^", 5, 0)
        self.create_button("=", 5, 1, columnspan=3)

    def create_button(self, text, row, col, columnspan=1):
        button = tk.Button(self.master, text=text, padx=40, pady=20, font=("Arial", 14),
                           command=lambda: self.on_button_click(text))
        button.grid(row=row, column=col, columnspan=columnspan, sticky="ew")

    def on_button_click(self, char):
        if char == "C":
            self.display.delete(0, tk.END)
        elif char == "=":
            try:
                expression = self.display.get().replace("^", "**")
                result = eval(expression)
                self.display.delete(0, tk.END)
                self.display.insert(0, str(result))
            except Exception:
                self.display.delete(0, tk.END)
                self.display.insert(0, "오류")
        else:
            self.display.insert(tk.END, char)

if __name__ == "__main__":
    root = tk.Tk()
    app = Calculator(root)
    root.mainloop()