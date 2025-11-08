import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import tkinter as tk
from tkinter import ttk, messagebox

from model.dbconection import conectar
from controller.paciente_controller import PacienteController


class PacienteView:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pacientes")
        self.root.geometry("820x460")
        self.root.resizable(False, False)

        # conexão/controller
        try:
            self.con = conectar()
            if not self.con:
                raise RuntimeError("Falha na conexão com o banco.")
            self.ctrl = PacienteController(self.con)
        except Exception as e:
            messagebox.showerror("Erro de conexão", str(e))
            return

        # formulário
        frm = tk.LabelFrame(self.root, text="Cadastro/edição", padx=8, pady=6)
        frm.place(x=10, y=10, width=800, height=160)

        tk.Label(frm, text="ID:").grid(row=0, column=0, sticky="w")
        self.ent_id = tk.Entry(frm, width=8, state="readonly")
        self.ent_id.grid(row=0, column=1, padx=(4, 16), sticky="w")

        tk.Label(frm, text="Nome:").grid(row=0, column=2, sticky="w")
        self.ent_nome = tk.Entry(frm, width=36)
        self.ent_nome.grid(row=0, column=3, padx=(4, 16), sticky="w")

        tk.Label(frm, text="CPF:").grid(row=1, column=2, sticky="w", pady=(6, 0))
        self.ent_cpf = tk.Entry(frm, width=22)
        self.ent_cpf.grid(row=1, column=3, padx=(4, 16), sticky="w", pady=(6, 0))

        tk.Label(frm, text="Data nasc. (AAAA-MM-DD):").grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.ent_nasc = tk.Entry(frm, width=16)
        self.ent_nasc.grid(row=1, column=1, padx=(4, 16), sticky="w", pady=(6, 0))

        tk.Label(frm, text="Telefone:").grid(row=2, column=0, sticky="w", pady=(6, 0))
        self.ent_tel = tk.Entry(frm, width=18)
        self.ent_tel.grid(row=2, column=1, padx=(4, 16), sticky="w", pady=(6, 0))

        tk.Button(frm, text="Novo", width=10, command=self.novo).grid(row=3, column=0, pady=10, sticky="w")
        tk.Button(frm, text="Salvar", width=12, command=self.salvar).grid(row=3, column=1, pady=10, sticky="w")
        tk.Button(frm, text="Excluir", width=10, command=self.excluir).grid(row=3, column=2, pady=10, sticky="w")

        # busca
        tk.Label(self.root, text="Buscar por nome:").place(x=12, y=180)
        self.ent_busca = tk.Entry(self.root, width=30)
        self.ent_busca.place(x=130, y=178)
        tk.Button(self.root, text="Buscar", command=self.buscar).place(x=340, y=175)
        tk.Button(self.root, text="Listar todos", command=self.carregar_tabela).place(x=410, y=175)

        # tabela
        cols = ("id", "nome", "cpf", "data_nascimento", "telefone")
        self.tree = ttk.Treeview(self.root, columns=cols, show="headings", height=12)
        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("cpf", text="CPF")
        self.tree.heading("data_nascimento", text="Data Nasc.")
        self.tree.heading("telefone", text="Telefone")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("nome", width=300)
        self.tree.column("cpf", width=140)
        self.tree.column("data_nascimento", width=120, anchor="center")
        self.tree.column("telefone", width=120)

        self.tree.place(x=10, y=210, width=800, height=230)
        vsb = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        vsb.place(x=810, y=210, height=230)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.bind("<Double-1>", self.on_double_click)

        # inicial
        self.carregar_tabela()
        self.ent_nome.focus()
        self.root.mainloop()

    # ações
    def novo(self):
        self.ent_id.configure(state="normal"); self.ent_id.delete(0, tk.END); self.ent_id.configure(state="readonly")
        self.ent_nome.delete(0, tk.END)
        self.ent_cpf.delete(0, tk.END)
        self.ent_nasc.delete(0, tk.END)
        self.ent_tel.delete(0, tk.END)
        self.ent_nome.focus()

    def salvar(self):
        nome = (self.ent_nome.get() or "").strip()
        cpf = (self.ent_cpf.get() or "").strip() or None
        nasc = (self.ent_nasc.get() or "").strip() or None
        tel  = (self.ent_tel.get() or "").strip() or None

        try:
            id_text = self.ent_id.get().strip()
            if id_text:
                ok = self.ctrl.atualizar_dados(int(id_text), nome, cpf, nasc, tel)
                if ok:
                    messagebox.showinfo("Sucesso", "Paciente atualizado.")
            else:
                new_id = self.ctrl.criar(nome, cpf=cpf, data_nascimento=nasc, telefone=tel)
                self.ent_id.configure(state="normal"); self.ent_id.insert(0, str(new_id)); self.ent_id.configure(state="readonly")
                messagebox.showinfo("Sucesso", f"Cadastrado com ID {new_id}.")
            self.carregar_tabela()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def excluir(self):
        id_text = self.ent_id.get().strip()
        if not id_text:
            messagebox.showwarning("Atenção", "Selecione um registro (duplo clique na tabela).")
            return
        if not messagebox.askyesno("Confirmar", "Excluir este paciente?"):
            return
        try:
            ok = self.ctrl.excluir(int(id_text))
            if ok:
                messagebox.showinfo("OK", "Excluído.")
                self.novo()
                self.carregar_tabela()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def carregar_tabela(self):
        rows = self.ctrl.listar()
        self.preencher_tree(rows)

    def buscar(self):
        termo = (self.ent_busca.get() or "").strip().lower()
        if not termo:
            self.carregar_tabela(); return
        todos = self.ctrl.listar()
        filtrados = [r for r in todos if termo in (r.get("nome") or "").lower()]
        self.preencher_tree(filtrados)

    def preencher_tree(self, rows):
        self.tree.delete(*self.tree.get_children())
        for r in rows:
            self.tree.insert("", tk.END, values=(
                r.get("id_paciente"),
                r.get("nome"),
                r.get("cpf"),
                str(r.get("data_nascimento")) if r.get("data_nascimento") else "",
                r.get("telefone") or ""
            ))

    def on_double_click(self, _event):
        item = self.tree.selection()
        if not item: return
        vals = self.tree.item(item[0], "values")
        self.ent_id.configure(state="normal"); self.ent_id.delete(0, tk.END); self.ent_id.insert(0, vals[0]); self.ent_id.configure(state="readonly")
        self.ent_nome.delete(0, tk.END); self.ent_nome.insert(0, vals[1])
        self.ent_cpf.delete(0, tk.END); self.ent_cpf.insert(0, vals[2] if vals[2] != "None" else "")
        self.ent_nasc.delete(0, tk.END); self.ent_nasc.insert(0, vals[3] if vals[3] != "None" else "")
        self.ent_tel.delete(0, tk.END); self.ent_tel.insert(0, vals[4] if vals[4] != "None" else "")


if __name__ == "__main__":
    PacienteView()
