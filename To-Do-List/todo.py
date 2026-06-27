import tkinter as tk
from tkinter import messagebox
import json, os
from datetime import datetime, timedelta

DATA_FILE    = "todos.json"
REMIND_AFTER = timedelta(minutes=1)

# ── Palette ────────────────────────────────────────────────────
BG       = "#f5f5f0"   # warm off-white page
CARD     = "#ffffff"   # card surface
ACCENT   = "#5c6bc0"   # indigo accent
DONE_COL = "#9e9e9e"   # muted for completed
TEXT     = "#2d2d2d"   # primary text
MUTED    = "#757575"   # secondary text
BORDER   = "#e0e0e0"   # hairline
SUCCESS  = "#43a047"   # green checkmark
DANGER   = "#e53935"   # red delete

def load():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return []

def save(todos):
    with open(DATA_FILE, "w") as f:
        json.dump(todos, f, indent=2)


class TodoApp:
    def __init__(self, root):
        self.root = root
        root.title("To-Do")
        root.geometry("480x580")
        root.resizable(False, False)
        root.configure(bg=BG)

        self.todos   = load()
        self.editing = None

        self.build_ui()
        self.refresh()
        self.check_reminders()

    # ── UI ─────────────────────────────────────────────────────
    def build_ui(self):
        # Header
        hdr = tk.Frame(self.root, bg=ACCENT)
        hdr.pack(fill="x")
        tk.Label(hdr, text="My To-Do List", font=("Segoe UI", 15, "bold"),
                 bg=ACCENT, fg="white").pack(pady=14)

        # Input card
        ic = tk.Frame(self.root, bg=CARD, bd=0,
                      highlightthickness=1, highlightbackground=BORDER)
        ic.pack(fill="x", padx=16, pady=(14, 0))

        self.task_var = tk.StringVar()
        self.entry = tk.Entry(ic, textvariable=self.task_var,
                              font=("Segoe UI", 11), bg=CARD, fg=TEXT,
                              relief="flat", bd=0, insertbackground=ACCENT)
        self.entry.pack(side="left", fill="x", expand=True, padx=12, ipady=10)
        self.entry.bind("<Return>", lambda e: self.save_task())
        self.entry.insert(0, "Add a new task…")
        self.entry.config(fg=MUTED)
        self.entry.bind("<FocusIn>",  self._clear_placeholder)
        self.entry.bind("<FocusOut>", self._restore_placeholder)

        self.save_btn = tk.Button(ic, text="Add", font=("Segoe UI", 10, "bold"),
                                  bg=ACCENT, fg="white", relief="flat", bd=0,
                                  padx=16, cursor="hand2",
                                  activebackground="#3f51b5", activeforeground="white",
                                  command=self.save_task)
        self.save_btn.pack(side="right", padx=6, pady=6)

        # Stats bar
        self.stats_var = tk.StringVar()
        tk.Label(self.root, textvariable=self.stats_var,
                 font=("Segoe UI", 9), bg=BG, fg=MUTED).pack(anchor="w", padx=18, pady=(8, 2))

        # Scrollable task list
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        self.canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        sb = tk.Scrollbar(outer, orient="vertical", command=self.canvas.yview)
        self.tasks_frame = tk.Frame(self.canvas, bg=BG)

        self.tasks_frame.bind("<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.tasks_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=sb.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>",
            lambda e: self.canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        # Bottom bar
        bar = tk.Frame(self.root, bg=CARD,
                       highlightthickness=1, highlightbackground=BORDER)
        bar.pack(fill="x", side="bottom")

        tk.Button(bar, text="🔔 Reminders", font=("Segoe UI", 9),
                  bg=CARD, fg=ACCENT, relief="flat", bd=0,
                  padx=12, pady=8, cursor="hand2",
                  command=self.manual_reminder,
                  activebackground=BG).pack(side="left")

        tk.Button(bar, text="Clear done", font=("Segoe UI", 9),
                  bg=CARD, fg=MUTED, relief="flat", bd=0,
                  padx=12, pady=8, cursor="hand2",
                  command=self.clear_done,
                  activebackground=BG).pack(side="right")

    # ── Placeholder helpers ────────────────────────────────────
    def _clear_placeholder(self, e):
        if self.entry.get() == "Add a new task…":
            self.entry.delete(0, "end")
            self.entry.config(fg=TEXT)

    def _restore_placeholder(self, e):
        if not self.entry.get():
            self.entry.insert(0, "Add a new task…")
            self.entry.config(fg=MUTED)

    # ── Save / update ──────────────────────────────────────────
    def save_task(self):
        text = self.task_var.get().strip()
        if not text or text == "Add a new task…":
            return

        if self.editing is not None:
            self.todos[self.editing]["text"] = text
            self.editing = None
            self.save_btn.config(text="Add", bg=ACCENT)
        else:
            self.todos.append({
                "text":     text,
                "done":     False,
                "created":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "reminded": False
            })

        self.task_var.set("")
        self._restore_placeholder(None)
        save(self.todos)
        self.refresh()

    def cancel_edit(self):
        self.editing = None
        self.task_var.set("")
        self._restore_placeholder(None)
        self.save_btn.config(text="Add", bg=ACCENT)

    # ── Task card ──────────────────────────────────────────────
    def make_card(self, index, task):
        done = task["done"]
        card = tk.Frame(self.tasks_frame, bg=CARD,
                        highlightthickness=1,
                        highlightbackground=BORDER)
        card.pack(fill="x", pady=3)

        # Left color bar
        bar_color = DONE_COL if done else ACCENT
        tk.Frame(card, bg=bar_color, width=4).pack(side="left", fill="y")

        # Checkbox area (drawn as a label that toggles)
        check_char = "✓" if done else "○"
        check_col  = SUCCESS if done else MUTED
        ck = tk.Label(card, text=check_char, font=("Segoe UI", 14),
                      bg=CARD, fg=check_col, cursor="hand2")
        ck.pack(side="left", padx=(10, 4), pady=10)
        ck.bind("<Button-1>", lambda e, i=index: self.toggle_done(i))

        # Text
        text_fg   = DONE_COL if done else TEXT
        text_font = ("Segoe UI", 10, "overstrike") if done else ("Segoe UI", 10)
        tk.Label(card, text=task["text"], font=text_font, fg=text_fg,
                 bg=CARD, anchor="w", wraplength=280, justify="left"
                 ).pack(side="left", fill="x", expand=True, pady=10)

        # Buttons
        if not done:
            tk.Button(card, text="✏", font=("Segoe UI", 11),
                      bg=CARD, fg=ACCENT, relief="flat", bd=0,
                      padx=6, cursor="hand2",
                      activebackground=BG,
                      command=lambda i=index, t=task: self.start_edit(i, t)
                      ).pack(side="right", padx=(0, 2))

        tk.Button(card, text="✕", font=("Segoe UI", 11),
                  bg=CARD, fg=DANGER, relief="flat", bd=0,
                  padx=6, cursor="hand2",
                  activebackground=BG,
                  command=lambda i=index: self.delete_task(i)
                  ).pack(side="right", padx=(0, 4))

    # ── Refresh ────────────────────────────────────────────────
    def refresh(self):
        for w in self.tasks_frame.winfo_children():
            w.destroy()

        if not self.todos:
            tk.Label(self.tasks_frame,
                     text="No tasks yet.\nType something above and press Add.",
                     font=("Segoe UI", 11), bg=BG, fg=MUTED,
                     justify="center").pack(pady=50)
        else:
            for i, task in enumerate(self.todos):
                self.make_card(i, task)

        total  = len(self.todos)
        done   = sum(1 for t in self.todos if t["done"])
        active = total - done
        self.stats_var.set(f"{active} active  •  {done} done  •  {total} total")

    # ── Actions ────────────────────────────────────────────────
    def toggle_done(self, index):
        self.todos[index]["done"] = not self.todos[index]["done"]
        save(self.todos)
        self.refresh()

    def start_edit(self, index, task):
        self.editing = index
        self.task_var.set(task["text"])
        self.entry.config(fg=TEXT)
        self.save_btn.config(text="Save", bg="#43a047")
        self.entry.focus_set()
        self.entry.icursor("end")

    def delete_task(self, index):
        if messagebox.askyesno("Delete task", "Remove this task?"):
            self.todos.pop(index)
            if self.editing == index:
                self.cancel_edit()
            save(self.todos)
            self.refresh()

    def clear_done(self):
        if any(t["done"] for t in self.todos):
            if messagebox.askyesno("Clear done", "Remove all completed tasks?"):
                self.todos = [t for t in self.todos if not t["done"]]
                save(self.todos)
                self.refresh()

    # ── Reminders ──────────────────────────────────────────────
    def check_reminders(self):
        now = datetime.now()
        due = []
        for task in self.todos:
            if task.get("done") or task.get("reminded"):
                continue
            try:
                created = datetime.strptime(task["created"], "%Y-%m-%d %H:%M:%S")
                if now - created >= REMIND_AFTER:
                    due.append(task["text"])
                    task["reminded"] = True
            except:
                pass
        if due:
            save(self.todos)
            messagebox.showinfo("Reminder",
                "You still have pending tasks:\n\n" +
                "\n".join(f"  • {t}" for t in due))
            self.refresh()
        self.root.after(60000, self.check_reminders)

    def manual_reminder(self):
        now = datetime.now()
        due = [t["text"] for t in self.todos
               if not t.get("done") and
               self._is_overdue(t["created"], now)]
        if due:
            messagebox.showinfo("Pending tasks",
                "\n".join(f"  • {t}" for t in due))
        else:
            messagebox.showinfo("All clear", "No overdue tasks right now!")

    def _is_overdue(self, created_str, now):
        try:
            return now - datetime.strptime(created_str, "%Y-%m-%d %H:%M:%S") >= REMIND_AFTER
        except:
            return False


if __name__ == "__main__":
    root = tk.Tk()
    TodoApp(root)
    root.mainloop()