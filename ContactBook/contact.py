import tkinter as tk
from tkinter import messagebox
import json
import os

DATA_FILE = "contacts.json"

BG     = "#f5f5f0"
CARD   = "#ffffff"
ACCENT = "#3095bd"
TEXT   = "#2d2d2d"
MUTED  = "#757575"
BORDER = "#e0e0e0"
RED    = "#e53935"

def load():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return []

def save(contacts):
    with open(DATA_FILE, "w") as f:
        json.dump(contacts, f, indent=2)


class ContactBook:
    def __init__(self, root):
        self.root = root
        root.title("Contact Book")
        root.geometry("720x540")
        root.resizable(False, False)
        root.configure(bg=BG)

        self.contacts = load()
        self.selected = None
        self.editing  = False

        self._build_ui()
        self._refresh_list()

    def _build_ui(self):
        hdr = tk.Frame(self.root, bg=ACCENT)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Contact Book", font=("Segoe UI", 14, "bold"),
                 bg=ACCENT, fg="white").pack(side="left", padx=16, pady=12)

        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True)

        left = tk.Frame(main, bg=BG, width=260)
        left.pack(side="left", fill="y", padx=(14, 6), pady=14)
        left.pack_propagate(False)

        search_frame = tk.Frame(left, bg=CARD,
                                highlightthickness=1, highlightbackground=BORDER)
        search_frame.pack(fill="x", pady=(0, 8))

        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self._refresh_list())
        tk.Entry(search_frame, textvariable=self.search_var,
                 font=("Segoe UI", 11), bg=CARD, fg=TEXT,
                 relief="flat", bd=0,
                 insertbackground=ACCENT).pack(fill="x", padx=10, ipady=8)

        tk.Label(left, text="CONTACTS", font=("Segoe UI", 8, "bold"),
                 bg=BG, fg=MUTED).pack(anchor="w", pady=(0, 4))

        list_frame = tk.Frame(left, bg=CARD,
                              highlightthickness=1, highlightbackground=BORDER)
        list_frame.pack(fill="both", expand=True)

        sb = tk.Scrollbar(list_frame)
        sb.pack(side="right", fill="y")

        self.listbox = tk.Listbox(list_frame, yscrollcommand=sb.set,
                                  font=("Segoe UI", 11), bg=CARD, fg=TEXT,
                                  relief="flat", bd=0,
                                  selectbackground=ACCENT, selectforeground="white",
                                  activestyle="none", cursor="hand2")
        self.listbox.pack(fill="both", expand=True)
        sb.config(command=self.listbox.yview)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        tk.Button(left, text="New Contact",
                  font=("Segoe UI", 10, "bold"),
                  bg=ACCENT, fg="white", relief="flat", bd=0,
                  pady=9, cursor="hand2",
                  activebackground="#3f51b5", activeforeground="white",
                  command=self._new_contact).pack(fill="x", pady=(8, 0))

        right = tk.Frame(main, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=(6, 14), pady=14)

        self.detail_card = tk.Frame(right, bg=CARD,
                                    highlightthickness=1, highlightbackground=BORDER)
        self.detail_card.pack(fill="both", expand=True)

        self.avatar_lbl = tk.Label(self.detail_card, text="",
                                   font=("Segoe UI", 36),
                                   bg=MUTED, fg="white", width=3)
        self.avatar_lbl.pack(fill="x")

        form = tk.Frame(self.detail_card, bg=CARD)
        form.pack(fill="both", expand=True, padx=20, pady=16)

        self.vars = {}
        fields = [("Name", "name"), ("Phone", "phone"),
                  ("Email", "email"), ("Address", "address")]

        for label, key in fields:
            tk.Label(form, text=label.upper(), font=("Segoe UI", 8, "bold"),
                     bg=CARD, fg=MUTED).pack(anchor="w", pady=(8, 2))
            v = tk.StringVar()
            e = tk.Entry(form, textvariable=v,
                         font=("Segoe UI", 11), bg=BG, fg=TEXT,
                         relief="flat", bd=0, insertbackground=ACCENT,
                         state="disabled", disabledbackground=BG,
                         disabledforeground=TEXT)
            e.pack(fill="x", ipady=6, pady=(0, 2))
            tk.Frame(form, bg=BORDER, height=1).pack(fill="x")
            self.vars[key] = (v, e)

        btn_row = tk.Frame(self.detail_card, bg=CARD)
        btn_row.pack(fill="x", padx=20, pady=(4, 20))

        self.edit_btn = tk.Button(btn_row, text="Edit",
                                  font=("Segoe UI", 10),
                                  bg=ACCENT, fg="white", relief="flat", bd=0,
                                  padx=18, pady=8, cursor="hand2",
                                  activebackground="#3f51b5",
                                  command=self._toggle_edit,
                                  state="disabled")
        self.edit_btn.pack(side="left", padx=(0, 8))

        self.save_btn = tk.Button(btn_row, text="Save",
                                  font=("Segoe UI", 10),
                                  bg="#43a047", fg="white", relief="flat", bd=0,
                                  padx=18, pady=8, cursor="hand2",
                                  activebackground="#2e7d32",
                                  command=self._save_contact,
                                  state="disabled")
        self.save_btn.pack(side="left", padx=(0, 8))

        self.del_btn = tk.Button(btn_row, text="Delete",
                                 font=("Segoe UI", 10),
                                 bg=CARD, fg=RED, relief="flat", bd=0,
                                 padx=18, pady=8, cursor="hand2",
                                 highlightthickness=1, highlightbackground=RED,
                                 activebackground="#ffebee",
                                 command=self._delete_contact,
                                 state="disabled")
        self.del_btn.pack(side="left")

    def _show_placeholder(self):
        self.avatar_lbl.config(text="", bg=MUTED)
        for key, (v, e) in self.vars.items():
            v.set("")
            e.config(state="disabled")
        self.edit_btn.config(state="disabled")
        self.save_btn.config(state="disabled")
        self.del_btn.config(state="disabled")

    def _refresh_list(self):
        q = self.search_var.get().lower()
        self.listbox.delete(0, "end")
        self.filtered = []
        for c in self.contacts:
            if q in c["name"].lower() or q in c["phone"].lower():
                self.listbox.insert("end", f"  {c['name']}")
                self.filtered.append(c)
        if not self.filtered:
            self.listbox.insert("end", "  No contacts found")

    def _on_select(self, event):
        sel = self.listbox.curselection()
        if not sel or not self.filtered:
            return
        idx = sel[0]
        if idx >= len(self.filtered):
            return
        self.selected = self.filtered[idx]
        self.editing  = False
        self._load_fields(self.selected)
        self._set_edit_mode(False)

    def _load_fields(self, contact):
        init = contact["name"][0].upper() if contact["name"] else "?"
        self.avatar_lbl.config(text=init, bg=ACCENT)
        for key, (v, e) in self.vars.items():
            v.set(contact.get(key, ""))

    def _set_edit_mode(self, editing):
        state = "normal" if editing else "disabled"
        bg    = CARD if editing else BG
        for key, (v, e) in self.vars.items():
            e.config(state=state, bg=bg, disabledbackground=BG)
        self.edit_btn.config(text="Cancel" if editing else "Edit",
                             bg=MUTED if editing else ACCENT,
                             state="normal")
        self.save_btn.config(state="normal" if editing else "disabled")
        self.del_btn.config(state="disabled" if editing else "normal")
        self.editing = editing

    def _toggle_edit(self):
        if self.editing:
            if self.selected:
                self._load_fields(self.selected)
            self._set_edit_mode(False)
        else:
            self._set_edit_mode(True)

    def _save_contact(self):
        name  = self.vars["name"][0].get().strip()
        phone = self.vars["phone"][0].get().strip()
        if not name or not phone:
            messagebox.showwarning("Missing info", "Name and Phone are required.")
            return

        data = {k: self.vars[k][0].get().strip() for k in self.vars}

        if self.selected is None:
            self.contacts.append(data)
            self.selected = data
        else:
            idx = self.contacts.index(self.selected)
            self.contacts[idx] = data
            self.selected = data

        save(self.contacts)
        self._refresh_list()
        self._set_edit_mode(False)
        self._load_fields(self.selected)

    def _delete_contact(self):
        if self.selected is None:
            return
        if messagebox.askyesno("Delete", f"Delete '{self.selected['name']}'?"):
            self.contacts.remove(self.selected)
            save(self.contacts)
            self.selected = None
            self._refresh_list()
            self._show_placeholder()

    def _new_contact(self):
        self.selected = None
        self.listbox.selection_clear(0, "end")
        self.avatar_lbl.config(text="?", bg=MUTED)
        for key, (v, e) in self.vars.items():
            v.set("")
        self._set_edit_mode(True)
        self.del_btn.config(state="disabled")
        self.vars["name"][1].focus_set()


if __name__ == "__main__":
    root = tk.Tk()
    ContactBook(root)
    root.mainloop()