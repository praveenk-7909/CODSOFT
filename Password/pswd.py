import tkinter as tk
from tkinter import messagebox
import random
import string

# ── Palette ────────────────────────────────────────────────────
BG      = "#f5f5f0"
CARD    = "#ffffff"
ACCENT  = "#5c6bc0"
TEXT    = "#2d2d2d"
MUTED   = "#757575"
BORDER  = "#e0e0e0"
GREEN   = "#43a047"
AMBER   = "#fb8c00"
RED     = "#e53935"
BLUE    = "#1976d2"

STRENGTH_COLORS = ["#e0e0e0", RED, AMBER, GREEN, BLUE]
STRENGTH_LABELS = ["", "Weak", "Fair", "Strong", "Very strong"]

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        root.title("Password Generator")
        root.geometry("420x480")
        root.resizable(False, False)
        root.configure(bg=BG)

        self.length_var  = tk.IntVar(value=16)
        self.use_upper   = tk.BooleanVar(value=True)
        self.use_lower   = tk.BooleanVar(value=True)
        self.use_digits  = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)

        self._build_ui()
        self._generate()

    def _build_ui(self):
        # Header
        tk.Frame(self.root, bg=ACCENT).pack(fill="x")
        tk.Label(self.root, text="Password Generator",
                 font=("Segoe UI", 14, "bold"),
                 bg=ACCENT, fg="white").place(x=0, y=0, relwidth=1)
        hdr = tk.Frame(self.root, bg=ACCENT)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Password Generator",
                 font=("Segoe UI", 14, "bold"),
                 bg=ACCENT, fg="white").pack(pady=12)

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=20, pady=12)

        # ── Length ────────────────────────────────────────────
        len_frame = tk.Frame(body, bg=CARD,
                             highlightthickness=1, highlightbackground=BORDER)
        len_frame.pack(fill="x", pady=(0, 10))

        top = tk.Frame(len_frame, bg=CARD)
        top.pack(fill="x", padx=14, pady=(12, 4))
        tk.Label(top, text="Length", font=("Segoe UI", 10),
                 bg=CARD, fg=MUTED).pack(side="left")
        self.len_label = tk.Label(top, text="16",
                                  font=("Segoe UI", 12, "bold"),
                                  bg=CARD, fg=ACCENT)
        self.len_label.pack(side="right")

        self.slider = tk.Scale(
            len_frame, from_=6, to=32,
            variable=self.length_var, orient="horizontal",
            bg=CARD, fg=TEXT, troughcolor=BORDER,
            highlightthickness=0, showvalue=False,
            command=self._on_length
        )
        self.slider.pack(fill="x", padx=14, pady=(0, 12))

        # ── Checkboxes ────────────────────────────────────────
        opt_frame = tk.Frame(body, bg=CARD,
                             highlightthickness=1, highlightbackground=BORDER)
        opt_frame.pack(fill="x", pady=(0, 10))
        tk.Label(opt_frame, text="Include", font=("Segoe UI", 9),
                 bg=CARD, fg=MUTED).pack(anchor="w", padx=14, pady=(10, 4))

        grid = tk.Frame(opt_frame, bg=CARD)
        grid.pack(fill="x", padx=14, pady=(0, 12))

        opts = [
            ("Uppercase  A–Z",  self.use_upper),
            ("Lowercase  a–z",  self.use_lower),
            ("Numbers   0–9",   self.use_digits),
            ("Symbols  !@#…",   self.use_symbols),
        ]
        for i, (label, var) in enumerate(opts):
            tk.Checkbutton(
                grid, text=label, variable=var,
                font=("Segoe UI", 10), bg=CARD, fg=TEXT,
                selectcolor=CARD, activebackground=CARD,
                command=self._generate, cursor="hand2"
            ).grid(row=i // 2, column=i % 2, sticky="w", padx=4, pady=2)

        # ── Password display ──────────────────────────────────
        disp = tk.Frame(body, bg=CARD,
                        highlightthickness=1, highlightbackground=BORDER)
        disp.pack(fill="x", pady=(0, 10))

        self.pwd_var = tk.StringVar()
        pwd_entry = tk.Entry(
            disp, textvariable=self.pwd_var,
            font=("Courier New", 13), bg=CARD, fg=TEXT,
            relief="flat", bd=0, state="readonly",
            readonlybackground=CARD, justify="center"
        )
        pwd_entry.pack(fill="x", padx=14, ipady=10, pady=(12, 4))

        # Strength bar (4 segments)
        bar_row = tk.Frame(disp, bg=CARD)
        bar_row.pack(fill="x", padx=14, pady=(0, 4))
        self.bars = []
        for _ in range(4):
            b = tk.Frame(bar_row, bg=BORDER, height=5)
            b.pack(side="left", fill="x", expand=True, padx=2)
            self.bars.append(b)

        self.strength_label = tk.Label(disp, text="",
                                       font=("Segoe UI", 9),
                                       bg=CARD, fg=MUTED)
        self.strength_label.pack(pady=(0, 10))

        # ── Buttons ───────────────────────────────────────────
        btn_row = tk.Frame(body, bg=BG)
        btn_row.pack(fill="x")

        tk.Button(
            btn_row, text="Generate",
            font=("Segoe UI", 10, "bold"),
            bg=ACCENT, fg="white", relief="flat", bd=0,
            padx=20, pady=9, cursor="hand2",
            activebackground="#3f51b5", activeforeground="white",
            command=self._generate
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))

        tk.Button(
            btn_row, text="Copy",
            font=("Segoe UI", 10),
            bg=CARD, fg=ACCENT, relief="flat", bd=0,
            padx=20, pady=9, cursor="hand2",
            highlightthickness=1, highlightbackground=ACCENT,
            activebackground=BG,
            command=self._copy
        ).pack(side="left", expand=True, fill="x")

    # ── Logic ──────────────────────────────────────────────────
    def _on_length(self, val):
        self.len_label.config(text=str(int(float(val))))
        self._generate()

    def _generate(self, *_):
        pool = ""
        guaranteed = []
        if self.use_upper.get():
            pool += string.ascii_uppercase
            guaranteed.append(random.choice(string.ascii_uppercase))
        if self.use_lower.get():
            pool += string.ascii_lowercase
            guaranteed.append(random.choice(string.ascii_lowercase))
        if self.use_digits.get():
            pool += string.digits
            guaranteed.append(random.choice(string.digits))
        if self.use_symbols.get():
            syms = "!@#$%^&*()-_=+[]{}|;:,.<>?"
            pool += syms
            guaranteed.append(random.choice(syms))

        if not pool:
            self.pwd_var.set("Select at least one option")
            self._set_strength(0)
            return

        length = self.length_var.get()
        remaining = length - len(guaranteed)
        pwd_chars = guaranteed + [random.choice(pool) for _ in range(max(0, remaining))]
        random.shuffle(pwd_chars)
        pwd = "".join(pwd_chars[:length])

        self.pwd_var.set(pwd)
        self._set_strength(self._score(length, sum([
            self.use_upper.get(), self.use_lower.get(),
            self.use_digits.get(), self.use_symbols.get()
        ])))

    def _score(self, length, sets):
        if length >= 20 and sets == 4: return 4
        if length >= 14 and sets >= 3: return 3
        if length >= 10 and sets >= 2: return 2
        return 1

    def _set_strength(self, score):
        color = STRENGTH_COLORS[score]
        for i, bar in enumerate(self.bars):
            bar.config(bg=color if i < score else BORDER)
        self.strength_label.config(
            text=STRENGTH_LABELS[score],
            fg=color if score else MUTED
        )

    def _copy(self):
        pwd = self.pwd_var.get()
        if pwd and pwd != "Select at least one option":
            self.root.clipboard_clear()
            self.root.clipboard_append(pwd)
            messagebox.showinfo("Copied", "Password copied to clipboard!")


if __name__ == "__main__":
    root = tk.Tk()
    PasswordGenerator(root)
    root.mainloop()