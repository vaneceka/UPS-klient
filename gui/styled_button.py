import tkinter as tk

class StyledButton(tk.Label):
    def __init__(self, parent, text, bg_color="#4CAF50", hover_color="#45A049",
                 text_color="white", font=("Arial", 13, "bold"),
                 command=None, padx=25, pady=8):
        super().__init__(
            parent,
            text=text,
            bg=bg_color,
            fg=text_color,
            font=font,
            padx=padx,
            pady=pady,
            cursor="hand2"
        )
        self.default_bg = bg_color
        self.hover_bg = hover_color
        self.command = command

        # Hover efekty
        self.bind("<Enter>", lambda e: self.config(bg=self.hover_bg))
        self.bind("<Leave>", lambda e: self.config(bg=self.default_bg))
        self.bind("<Button-1>", lambda e: self._on_click())

    def _on_click(self):
        if self.command:
            self.command()