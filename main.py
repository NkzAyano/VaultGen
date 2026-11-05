
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import base64
import secrets
import string
import shutil

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidTag

# ==========================================
# NKZ PASSWORD VAULT
# Secure Password Manager
# ==========================================

APP_NAME = "NKZ PASSWORD VAULT"
VAULT_FILE = "nkz_vault.json"
ITERATIONS = 600000

BG = "#090b14"
PANEL = "#111625"
PANEL2 = "#192136"
PURPLE = "#985cff"
BLUE = "#398cff"
WHITE = "#f4f5ff"
GRAY = "#929bb2"
GREEN = "#35d6a0"
RED = "#ff5574"


def derive_key(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS
    )
    return kdf.derive(password.encode("utf-8"))


class PasswordVault:

    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("1050x680")
        self.root.minsize(800, 550)
        self.root.configure(bg=BG)

        self.key = None
        self.entries = []
        self.show_passwords = False
        self.search_var = tk.StringVar()

        self.render_login()

    # ======================================
    # CRYPTOGRAPHY
    # ======================================

    def save_vault(self):
        salt = self.salt
        nonce = secrets.token_bytes(12)

        data = json.dumps(
            self.entries,
            ensure_ascii=False
        ).encode("utf-8")

        encrypted = AESGCM(self.key).encrypt(
            nonce, data, None
        )

        vault = {
            "version": 1,
            "salt": base64.b64encode(salt).decode(),
            "nonce": base64.b64encode(nonce).decode(),
            "data": base64.b64encode(encrypted).decode()
        }

        temp_file = VAULT_FILE + ".tmp"

        with open(temp_file, "w", encoding="utf-8") as file:
            json.dump(vault, file)

        os.replace(temp_file, VAULT_FILE)

    def load_vault(self, password):
        with open(VAULT_FILE, "r", encoding="utf-8") as file:
            vault = json.load(file)

        if vault.get("version") != 1:
            raise ValueError("Versao do cofre nao suportada.")

        self.salt = base64.b64decode(vault["salt"])
        nonce = base64.b64decode(vault["nonce"])
        encrypted = base64.b64decode(vault["data"])

        self.key = derive_key(password, self.salt)

        decrypted = AESGCM(self.key).decrypt(
            nonce, encrypted, None
        )

        self.entries = json.loads(decrypted.decode("utf-8"))

    # ======================================
    # INTERFACE HELPERS
    # ======================================

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def label(self, parent, text, size=11, color=WHITE, bold=False):
        return tk.Label(
            parent,
            text=text,
            bg=parent.cget("bg"),
            fg=color,
            font=("Segoe UI", size, "bold" if bold else "normal")
        )

    def button(self, parent, text, command, color=PANEL2):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg=WHITE,
            activebackground=PURPLE,
            activeforeground=WHITE,
            relief="flat",
            cursor="hand2",
            padx=13,
            pady=9,
            font=("Segoe UI", 9, "bold")
        )

    def make_entry(self, parent, show=None):
        return tk.Entry(
            parent,
            bg=PANEL2,
            fg=WHITE,
            insertbackground=WHITE,
            relief="flat",
            font=("Segoe UI", 11),
            show=show
        )

    # ======================================
    # LOGIN / MASTER PASSWORD
    # ======================================

    def render_login(self):
        self.clear_screen()

        frame = tk.Frame(self.root, bg=PANEL, padx=38, pady=35)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            frame,
            text="NKZ",
            bg=PANEL,
            fg=PURPLE,
            font=("Segoe UI", 34, "bold")
        ).pack()

        tk.Label(
            frame,
            text="PASSWORD VAULT",
            bg=PANEL,
            fg=WHITE,
            font=("Segoe UI", 16, "bold")
        ).pack(pady=(0, 5))

        self.label(
            frame,
            "SECURE PERSONAL PASSWORD MANAGER",
            9, GRAY
        ).pack(pady=(0, 25))

        exists = os.path.exists(VAULT_FILE)

        self.label(
            frame,
            "Digite sua senha mestra" if exists
            else "Crie sua senha mestra",
            10
        ).pack(anchor="w")

        self.master_entry = self.make_entry(frame, "*")
        self.master_entry.pack(fill="x", pady=8, ipady=8)
        self.master_entry.bind("<Return>", lambda e: self.authenticate())

        self.confirm_entry = None

        if not exists:
            self.label(frame, "Confirme a senha mestra", 10).pack(anchor="w")

            self.confirm_entry = self.make_entry(frame, "*")
            self.confirm_entry.pack(fill="x", pady=8, ipady=8)

        self.button(
            frame,
            "DESBLOQUEAR COFRE" if exists else "CRIAR COFRE",
            self.authenticate,
            PURPLE
        ).pack(fill="x", pady=15)

        self.label(
            frame,
            "NKZ CYBERSECURITY | LOCAL VAULT",
            8, GRAY
        ).pack(pady=(8, 0))

        self.master_entry.focus()

    def authenticate(self):
        password = self.master_entry.get()

        if len(password) < 8:
            messagebox.showwarning(
                "Senha invalida",
                "Use pelo menos 8 caracteres."
            )
            return

        if not os.path.exists(VAULT_FILE):
            confirmation = self.confirm_entry.get()

            if password != confirmation:
                messagebox.showerror(
                    "Erro",
                    "As senhas nao correspondem."
                )
                return

            self.salt = secrets.token_bytes(16)
            self.key = derive_key(password, self.salt)
            self.entries = []

            try:
                self.save_vault()
            except Exception as error:
                messagebox.showerror("Erro", str(error))
                return

        else:
            try:
                self.load_vault(password)
            except InvalidTag:
                self.key = None
                messagebox.showerror(
                    "Acesso negado",
                    "Senha mestra incorreta ou cofre danificado."
                )
                return
            except Exception as error:
                self.key = None
                messagebox.showerror("Erro", str(error))
                return

        self.render_dashboard()

    # ======================================
    # DASHBOARD
    # ======================================

    def render_dashboard(self):
        self.clear_screen()

        header = tk.Frame(self.root, bg=BG, padx=25, pady=20)
        header.pack(fill="x")

        tk.Label(
            header,
            text="NKZ",
            bg=BG,
            fg=PURPLE,
            font=("Segoe UI", 23, "bold")
        ).pack(side="left")

        tk.Label(
            header,
            text=" PASSWORD VAULT",
            bg=BG,
            fg=WHITE,
            font=("Segoe UI", 15, "bold")
        ).pack(side="left")

        self.button(
            header, "BLOQUEAR", self.lock, RED
        ).pack(side="right")

        content = tk.Frame(self.root, bg=BG, padx=25)
        content.pack(fill="both", expand=True)

        stats = tk.Frame(content, bg=BG)
        stats.pack(fill="x", pady=(5, 18))

        self.stat_label(stats, "CREDENCIAIS", len(self.entries))
        self.stat_label(
            stats, "CATEGORIAS",
            len(set(x.get("category", "Outros") for x in self.entries))
        )
        self.stat_label(stats, "STATUS", "PROTEGIDO")

        toolbar = tk.Frame(content, bg=BG)
        toolbar.pack(fill="x", pady=8)

        search = tk.Entry(
            toolbar,
            textvariable=self.search_var,
            bg=PANEL,
            fg=WHITE,
            insertbackground=WHITE,
            relief="flat",
            font=("Segoe UI", 11)
        )
        search.pack(side="left", fill="x", expand=True, ipady=10)
        search.insert(0, "")

        self.search_var.trace_add(
            "write", lambda *args: self.refresh_table()
        )

        self.button(
            toolbar, "+ ADICIONAR", self.add_entry, PURPLE
        ).pack(side="left", padx=7)

        table_frame = tk.Frame(content, bg=PANEL)
        table_frame.pack(fill="both", expand=True, pady=10)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background=PANEL,
            foreground=WHITE,
            fieldbackground=PANEL,
            rowheight=34,
            borderwidth=0,
            font=("Segoe UI", 10)
        )
        style.configure(
            "Treeview.Heading",
            background=PANEL2,
            foreground=WHITE,
            font=("Segoe UI", 9, "bold"),
            relief="flat"
        )
        style.map(
            "Treeview",
            background=[("selected", PURPLE)],
            foreground=[("selected", WHITE)]
        )

        columns = ("site", "user", "category", "password")

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        self.table.heading("site", text="CONTA / SITE")
        self.table.heading("user", text="USUARIO")
        self.table.heading("category", text="CATEGORIA")
        self.table.heading("password", text="SENHA")

        self.table.column("site", width=210)
        self.table.column("user", width=210)
        self.table.column("category", width=140)
        self.table.column("password", width=170)

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.table.yview
        )
        self.table.configure(yscrollcommand=scrollbar.set)

        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.table.bind("<Double-1>", lambda e: self.edit_entry())

        actions = tk.Frame(content, bg=BG)
        actions.pack(fill="x", pady=10)

        self.button(actions, "EDITAR", self.edit_entry).pack(side="left", padx=3)
        self.button(actions, "EXCLUIR", self.delete_entry, RED).pack(side="left", padx=3)
        self.button(actions, "COPIAR SENHA", self.copy_password).pack(side="left", padx=3)

        self.button(
            actions,
            "MOSTRAR / OCULTAR",
            self.toggle_passwords
        ).pack(side="left", padx=3)

        self.button(
            actions,
            "GERAR SENHA",
            self.generate_password,
            BLUE
        ).pack(side="left", padx=3)

        self.button(
            actions,
            "BACKUP",
            self.backup
        ).pack(side="right", padx=3)

        self.label(
            content,
            "NKZ CYBERSECURITY | AES-256-GCM | OFFLINE",
            8, GRAY
        ).pack(pady=8)

        self.refresh_table()

    def stat_label(self, parent, title, value):
        frame = tk.Frame(
            parent, bg=PANEL, padx=18, pady=14,
            highlightbackground="#292e43",
            highlightthickness=1
        )
        frame.pack(side="left", fill="x", expand=True, padx=5)

        self.label(frame, title, 8, GRAY).pack(anchor="w")
        self.label(frame, str(value), 16, PURPLE, True).pack(anchor="w")

    # ======================================
    # TABLE
    # ======================================

    def selected_index(self):
        selected = self.table.selection()

        if not selected:
            return None

        return int(selected[0])

    def refresh_table(self):
        if not hasattr(self, "table"):
            return

        for item in self.table.get_children():
            self.table.delete(item)

        query = self.search_var.get().lower()

        for index, entry in enumerate(self.entries):
            searchable = (
                entry.get("site", "") + " " +
                entry.get("username", "") + " " +
                entry.get("category", "")
            ).lower()

            if query not in searchable:
                continue

            password = entry.get("password", "")
            displayed = password if self.show_passwords else "********"

            self.table.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    entry.get("site", ""),
                    entry.get("username", ""),
                    entry.get("category", ""),
                    displayed
                )
            )

    # ======================================
    # ADD / EDIT
    # ======================================

    def add_entry(self):
        self.entry_window()

    def edit_entry(self):
        index = self.selected_index()

        if index is None:
            messagebox.showinfo("NKZ", "Selecione uma credencial.")
            return

        self.entry_window(index)

    def entry_window(self, index=None):
        editing = index is not None

        window = tk.Toplevel(self.root)
        window.title("Editar credencial" if editing else "Nova credencial")
        window.geometry("430x550")
        window.configure(bg=BG)
        window.resizable(False, False)
        window.transient(self.root)
        window.grab_set()

        entry = self.entries[index].copy() if editing else {
            "site": "",
            "username": "",
            "password": "",
            "category": "Outros",
            "notes": ""
        }

        tk.Label(
            window,
            text="EDITAR CREDENCIAL" if editing else "NOVA CREDENCIAL",
            bg=BG,
            fg=PURPLE,
            font=("Segoe UI", 17, "bold")
        ).pack(pady=20)

        fields = {}

        def create_field(title, key, secret=False):
            tk.Label(
                window, text=title,
                bg=BG, fg=GRAY,
                font=("Segoe UI", 9)
            ).pack(anchor="w", padx=35)

            field = tk.Entry(
                window,
                bg=PANEL,
                fg=WHITE,
                insertbackground=WHITE,
                relief="flat",
                font=("Segoe UI", 11),
                show="*" if secret else ""
            )
            field.pack(fill="x", padx=35, pady=(5, 12), ipady=8)
            field.insert(0, entry.get(key, ""))
            fields[key] = field

        create_field("NOME DA CONTA / SITE", "site")
        create_field("USUARIO / EMAIL", "username")
        create_field("SENHA", "password", True)

        tk.Label(
            window, text="CATEGORIA",
            bg=BG, fg=GRAY
        ).pack(anchor="w", padx=35)

        category = ttk.Combobox(
            window,
            values=[
                "Outros", "Redes sociais", "Jogos",
                "Trabalho", "Email", "Bancos", "Estudos"
            ],
            state="normal"
        )
        category.set(entry.get("category", "Outros"))
        category.pack(fill="x", padx=35, pady=(5, 12), ipady=5)

        create_field("OBSERVACOES", "notes")

        def save():
            site = fields["site"].get().strip()
            password = fields["password"].get()

            if not site or not password:
                messagebox.showwarning(
                    "Campos obrigatorios",
                    "Preencha o nome da conta e a senha.",
                    parent=window
                )
                return

            new_entry = {
                "site": site,
                "username": fields["username"].get().strip(),
                "password": password,
                "category": category.get().strip() or "Outros",
                "notes": fields["notes"].get().strip()
            }

            if editing:
                self.entries[index] = new_entry
            else:
                self.entries.append(new_entry)

            try:
                self.save_vault()
            except Exception as error:
                messagebox.showerror("Erro ao salvar", str(error))
                return

            window.destroy()
            self.refresh_table()
            messagebox.showinfo("NKZ", "Credencial salva com sucesso!")

        self.button(
            window, "SALVAR CREDENCIAL", save, PURPLE
        ).pack(fill="x", padx=35, pady=15)

    # ======================================
    # DELETE / COPY / SHOW
    # ======================================

    def delete_entry(self):
        index = self.selected_index()

        if index is None:
            messagebox.showinfo("NKZ", "Selecione uma credencial.")
            return

        if messagebox.askyesno(
            "Confirmar exclusao",
            "Deseja realmente excluir esta credencial?"
        ):
            del self.entries[index]
            self.save_vault()
            self.refresh_table()

    def copy_password(self):
        index = self.selected_index()

        if index is None:
            messagebox.showinfo("NKZ", "Selecione uma credencial.")
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(
            self.entries[index]["password"]
        )
        messagebox.showinfo("NKZ", "Senha copiada!")

    def toggle_passwords(self):
        self.show_passwords = not self.show_passwords
        self.refresh_table()

    # ======================================
    # PASSWORD GENERATOR
    # ======================================

    def generate_password(self):
        alphabet = string.ascii_letters + string.digits + "!@#$%&*_-+?"

        while True:
            password = "".join(
                secrets.choice(alphabet) for _ in range(20)
            )

            if (
                any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in "!@#$%&*_-+?" for c in password)
            ):
                break

        window = tk.Toplevel(self.root)
        window.title("Gerador NKZ")
        window.geometry("420x190")
        window.configure(bg=BG)
        window.transient(self.root)
        window.grab_set()

        tk.Label(
            window,
            text="SENHA GERADA",
            bg=BG,
            fg=PURPLE,
            font=("Segoe UI", 16, "bold")
        ).pack(pady=15)

        result = tk.Entry(
            window,
            bg=PANEL,
            fg=GREEN,
            justify="center",
            font=("Consolas", 13),
            relief="flat"
        )
        result.pack(fill="x", padx=20, ipady=10)
        result.insert(0, password)

        def copy():
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("NKZ", "Senha copiada!", parent=window)

        self.button(window, "COPIAR SENHA", copy, PURPLE).pack(pady=15)

    # ======================================
    # BACKUP
    # ======================================

    def backup(self):
        destination = filedialog.asksaveasfilename(
            title="Salvar backup criptografado",
            defaultextension=".nkz",
            filetypes=[("NKZ Vault", "*.nkz")]
        )

        if not destination:
            return

        try:
            self.save_vault()
            shutil.copy2(VAULT_FILE, destination)
            messagebox.showinfo(
                "Backup",
                "Backup criptografado criado com sucesso!"
            )
        except Exception as error:
            messagebox.showerror("Erro", str(error))

    # ======================================
    # LOCK
    # ======================================

    def lock(self):
        self.key = None
        self.entries = []
        self.show_passwords = False
        self.search_var.set("")
        self.render_login()


# ==========================================
# START APPLICATION
# ==========================================

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordVault(root)
    root.mainloop()
