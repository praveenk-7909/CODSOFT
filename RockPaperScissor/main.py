import tkinter as tk
import random

# ── Palette ────────────────────────────────────────────────────
BG     = "#f5f5f0"
CARD   = "#ffffff"
ACCENT = "#912da0"
TEXT   = "#2d2d2d"
MUTED  = "#757575"
BORDER = "#e0e0e0"
GREEN  = "#2e7d32"
RED    = "#c62828"
AMBER  = "#e65100"

CHOICES = ["Rock", "Paper", "Scissors"]
ICONS   = {"Rock": "✊", "Paper": "✋", "Scissors": "✌️"}
BEATS   = {"Rock": "Scissors", "Scissors": "Paper", "Paper": "Rock"}


class RPS:
    def __init__(self, root):
        self.root = root
        root.title("Rock · Paper · Scissors")
        root.geometry("440x560")
        root.resizable(False, False)
        root.configure(bg=BG)

        self.score = {"You": 0, "Computer": 0, "Ties": 0}
        self._build_ui()

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self.root, bg=ACCENT)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Rock · Paper · Scissors",
                 font=("Segoe UI", 14, "bold"),
                 bg=ACCENT, fg="white").pack(pady=12)

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=20, pady=14)

        
        sb = tk.Frame(body, bg=BG)
        sb.pack(fill="x", pady=(0, 12))

        self.score_labels = {}
        for label in ("You", "Ties", "Computer"):
            col = tk.Frame(sb, bg=CARD,
                           highlightthickness=1, highlightbackground=BORDER)
            col.pack(side="left", expand=True, fill="x", padx=4)
            tk.Label(col, text=label, font=("Segoe UI", 9),
                     bg=CARD, fg=MUTED).pack(pady=(8, 2))
            lbl = tk.Label(col, text="0", font=("Segoe UI", 22, "bold"),
                           bg=CARD, fg=TEXT)
            lbl.pack(pady=(0, 8))
            self.score_labels[label] = lbl

        
        arena = tk.Frame(body, bg=CARD,
                         highlightthickness=1, highlightbackground=BORDER)
        arena.pack(fill="x", pady=(0, 14))

        hands = tk.Frame(arena, bg=CARD)
        hands.pack(pady=(16, 8))

        self.hand_you = tk.Label(hands, text="🤜", font=("Segoe UI", 48),
                                 bg=CARD)
        self.hand_you.pack(side="left", padx=16)

        tk.Label(hands, text="VS", font=("Segoe UI", 11),
                 bg=CARD, fg=MUTED).pack(side="left")

        self.hand_cpu = tk.Label(hands, text="🤛", font=("Segoe UI", 48),
                                 bg=CARD)
        self.hand_cpu.pack(side="left", padx=16)

        self.result_var = tk.StringVar(value="Pick a move below")
        self.result_lbl = tk.Label(arena, textvariable=self.result_var,
                                   font=("Segoe UI", 16, "bold"),
                                   bg=CARD, fg=TEXT)
        self.result_lbl.pack()

        self.sub_var = tk.StringVar(value="")
        tk.Label(arena, textvariable=self.sub_var,
                 font=("Segoe UI", 10), bg=CARD, fg=MUTED).pack(pady=(2, 14))

        
        btn_row = tk.Frame(body, bg=BG)
        btn_row.pack(fill="x", pady=(0, 12))

        for choice in CHOICES:
            f = tk.Frame(btn_row, bg=CARD,
                         highlightthickness=1, highlightbackground=BORDER)
            f.pack(side="left", expand=True, fill="x", padx=4)
            tk.Label(f, text=ICONS[choice], font=("Segoe UI", 32),
                     bg=CARD, cursor="hand2").pack(pady=(10, 4))
            tk.Label(f, text=choice, font=("Segoe UI", 10),
                     bg=CARD, fg=MUTED).pack(pady=(0, 10))
            f.bind("<Button-1>", lambda e, c=choice: self.play(c))
            for w in f.winfo_children():
                w.bind("<Button-1>", lambda e, c=choice: self.play(c))
            f.bind("<Enter>", lambda e, fr=f: fr.config(highlightbackground=ACCENT))
            f.bind("<Leave>", lambda e, fr=f: fr.config(highlightbackground=BORDER))

        #
        tk.Button(body, text="Reset scores",
                  font=("Segoe UI", 10), bg=CARD, fg=MUTED,
                  relief="flat", bd=0, pady=8,
                  highlightthickness=1, highlightbackground=BORDER,
                  cursor="hand2", activebackground=BG,
                  command=self.reset).pack(fill="x")

    def play(self, user):
        cpu = random.choice(CHOICES)

        self.hand_you.config(text=ICONS[user])
        self.hand_cpu.config(text=ICONS[cpu])
        self.sub_var.set(f"You chose {user}   •   Computer chose {cpu}")

        if user == cpu:
            msg, color = "It's a tie!", AMBER
            self.score["Ties"] += 1
        elif BEATS[user] == cpu:
            msg, color = "You win!", GREEN
            self.score["You"] += 1
        else:
            msg, color = "Computer wins!", RED
            self.score["Computer"] += 1

        self.result_var.set(msg)
        self.result_lbl.config(fg=color)

        for key, lbl in self.score_labels.items():
            lbl.config(text=str(self.score[key]))

    def reset(self):
        self.score = {"You": 0, "Computer": 0, "Ties": 0}
        for key, lbl in self.score_labels.items():
            lbl.config(text="0")
        self.hand_you.config(text="🤜")
        self.hand_cpu.config(text="🤛")
        self.result_var.set("Pick a move below")
        self.result_lbl.config(fg=TEXT)
        self.sub_var.set("")


if __name__ == "__main__":
    root = tk.Tk()
    RPS(root)
    root.mainloop()