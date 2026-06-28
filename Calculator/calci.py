import tkinter as tk

BG       = "#2b2b2b"
DISP_BG  = "#2b2b2b"
NUM_BG   = "#3c3c3c"
OP_BG    = "#be851a"
EQ_BG    = "#555555"
FUNC_BG  = "#3c3c3c"
NUM_FG   = "#ffffff"
OP_FG    = "#dddddd"
FUNC_FG  = "#cccccc"
DISP_FG  = "#ffffff"

class Calculator:
    def __init__(self, root):
        self.root = root
        root.title("Calculator")
        root.configure(bg=BG)
        root.resizable(False, False)

        self.expression = ""   
        self.just_evaled = False

        self._build_display()
        self._build_buttons()


    def _build_display(self):
        frame = tk.Frame(self.root, bg=DISP_BG)
        frame.pack(fill="x", padx=0, pady=0)

        self.expr_var = tk.StringVar(value="")
        tk.Label(frame, textvariable=self.expr_var,
                 font=("Segoe UI", 13), bg=DISP_BG, fg="#888888",
                 anchor="e", padx=16).pack(fill="x", pady=(14, 0))

        self.result_var = tk.StringVar(value="0")
        tk.Label(frame, textvariable=self.result_var,
                 font=("Segoe UI", 42, "bold"), bg=DISP_BG, fg=DISP_FG,
                 anchor="e", padx=16).pack(fill="x", pady=(0, 12))

    
    def _build_buttons(self):
        grid = tk.Frame(self.root, bg=BG)
        grid.pack(padx=8, pady=8)

        
        buttons = [
            ("AC",  0, 0, 1, FUNC_BG, FUNC_FG, "clear"),
            ("+/-", 1, 0, 1, FUNC_BG, FUNC_FG, "negate"),
            ("%",   2, 0, 1, FUNC_BG, FUNC_FG, "percent"),
            ("÷",   3, 0, 1, OP_BG,   OP_FG,   "/"),

            ("7",   0, 1, 1, NUM_BG,  NUM_FG,  "7"),
            ("8",   1, 1, 1, NUM_BG,  NUM_FG,  "8"),
            ("9",   2, 1, 1, NUM_BG,  NUM_FG,  "9"),
            ("×",   3, 1, 1, OP_BG,   OP_FG,   "*"),

            ("4",   0, 2, 1, NUM_BG,  NUM_FG,  "4"),
            ("5",   1, 2, 1, NUM_BG,  NUM_FG,  "5"),
            ("6",   2, 2, 1, NUM_BG,  NUM_FG,  "6"),
            ("−",   3, 2, 1, OP_BG,   OP_FG,   "-"),

            ("1",   0, 3, 1, NUM_BG,  NUM_FG,  "1"),
            ("2",   1, 3, 1, NUM_BG,  NUM_FG,  "2"),
            ("3",   2, 3, 1, NUM_BG,  NUM_FG,  "3"),
            ("+",   3, 3, 1, OP_BG,   OP_FG,   "+"),

            ("0",   0, 4, 2, NUM_BG,  NUM_FG,  "0"),   
            (".",   2, 4, 1, NUM_BG,  NUM_FG,  "."),
            ("=",   3, 4, 1, OP_BG,   OP_FG,   "="),
        ]

        BTN_W = 72
        BTN_H = 58

        for (label, col, row, span, bg, fg, action) in buttons:
            w = BTN_W * span + (span - 1) * 8
            btn = tk.Button(
                grid,
                text=label,
                font=("Segoe UI", 18, "bold"),
                bg=bg, fg=fg,
                activebackground=self._lighten(bg),
                activeforeground=fg,
                relief="flat", bd=0,
                width=1, height=1,
                cursor="hand2",
                command=lambda a=action: self.handle(a)
            )
            btn.grid(row=row, column=col, columnspan=span,
                     padx=4, pady=4, ipadx=0, ipady=0,
                     sticky="nsew")
            btn.config(width=w // 10)   

        for c in range(4):
            grid.columnconfigure(c, minsize=BTN_W, weight=1)
        for r in range(5):
            grid.rowconfigure(r, minsize=BTN_H, weight=1)

        self.root.bind("<Key>", self._key)

    def handle(self, action):
        expr = self.expression

        if action == "clear":
            self.expression = ""
            self.expr_var.set("")
            self.result_var.set("0")
            self.just_evaled = False
            return

        if action == "=":
            if not expr:
                return
            try:
                result = eval(expr)
                result = self._fmt(result)
                self.expr_var.set(expr + " =")
                self.result_var.set(result)
                self.expression = result
                self.just_evaled = True
            except ZeroDivisionError:
                self.result_var.set("Can't ÷ 0")
                self.expr_var.set(expr)
                self.expression = ""
            except Exception:
                self.result_var.set("Error")
                self.expression = ""
            return

        if action == "negate":
            if not expr:
                return
            try:
                val = self._fmt(-eval(expr))
                self.expression = val
                self.result_var.set(val)
                self.expr_var.set("")
            except:
                pass
            return

        if action == "percent":
            if not expr:
                return
            try:
                val = self._fmt(eval(expr) / 100)
                self.expression = val
                self.result_var.set(val)
                self.expr_var.set("")
            except:
                pass
            return

        if self.just_evaled and action not in ("+", "-", "*", "/"):
            self.expression = ""
            self.expr_var.set("")
        self.just_evaled = False

        if action in ("+", "-", "*", "/") and expr and expr[-1] in "+-*/":
            self.expression = expr[:-1] + action
        else:
            self.expression += action

        self.expr_var.set(self.expression)
        try:
            self.result_var.set(self._fmt(eval(self.expression)))
        except:
            self.result_var.set(self.expression)


    def _fmt(self, value):
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        rounded = round(value, 10)
        formatted = f"{rounded:.10f}".rstrip('0').rstrip('.')
        return formatted

    def _lighten(self, hex_color):
        r, g, b = int(hex_color[1:3],16), int(hex_color[3:5],16), int(hex_color[5:7],16)
        r, g, b = min(255, r+30), min(255, g+30), min(255, b+30)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _key(self, event):
        k = event.char
        mapping = {"0":"0","1":"1","2":"2","3":"3","4":"4",
                   "5":"5","6":"6","7":"7","8":"8","9":"9",
                   "+":"+","-":"-","*":"*","/":"/",".":".",
                   "\r":"=","\n":"=","\x08":"clear"}
        if k in mapping:
            self.handle(mapping[k])


if __name__ == "__main__":
    root = tk.Tk()
    Calculator(root)
    root.mainloop()