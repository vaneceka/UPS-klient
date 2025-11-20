import tkinter as tk
from gui.styled_button import StyledButton
from gui.utils import center_window


class GameOverWindow:
    def __init__(self, parent, result_text, color, on_restart, on_quit):
        """
        :param parent: rodičovské okno (CheckersGUI.root)
        :param result_text: text výsledku (např. 'Vyhrál jsi!')
        :param color: barva textu (zelená / červená)
        :param on_restart: callback funkce pro tlačítko 'Hrát znovu'
        :param on_quit: callback funkce pro tlačítko 'Ukončit hru'
        """
        self.win = tk.Toplevel(parent)
        self.win.title("Konec hry")
        self.win.configure(bg="#F5F5F5")
        self.win.resizable(False, False)

        center_window(self.win, 350, 280)

        # Výsledek
        label = tk.Label(
            self.win,
            text=result_text,
            font=("Arial", 16, "bold"),
            bg="#F5F5F5",
            fg=color
        )
        label.pack(pady=25)

        # Hrát znovu
        StyledButton(
            self.win,
            text="🔁 Hrát znovu",
            bg_color="#4CAF50",
            hover_color="#45A049",
            command=lambda: on_restart(self.win)
        ).pack(pady=6)

        # Ukončit hru
        StyledButton(
            self.win,
            text="🚪 Ukončit hru",
            bg_color="#E53935",
            hover_color="#C62828",
            command=lambda: on_quit(self.win)
        ).pack(pady=6)