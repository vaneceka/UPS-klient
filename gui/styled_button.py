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
        self.enabled = True  # ✅ nový příznak

        # Hover efekty
        self.bind("<Enter>", lambda e: self._on_hover(True))
        self.bind("<Leave>", lambda e: self._on_hover(False))
        self.bind("<Button-1>", lambda e: self._on_click())

    def _on_hover(self, is_entering):
        """Změna barvy při najetí, jen pokud je aktivní"""
        if not self.enabled:
            return
        self.config(bg=self.hover_bg if is_entering else self.default_bg)

    def _on_click(self):
        """Kliknutí — volá command jen pokud je aktivní"""
        if not self.enabled:
            return
        if self.command:
            self.command()

    def disable(self):
        """Zneaktivní tlačítko"""
        self.enabled = False
        self.config(bg="#888", cursor="arrow")

    def enable(self):
        """Znovu aktivuje tlačítko"""
        self.enabled = True
        self.config(bg=self.default_bg, cursor="hand2")