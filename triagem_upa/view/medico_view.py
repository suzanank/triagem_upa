import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import tkinter as tk
from tkinter import ttk, messagebox

from model.dbconection import conectar
from controller.medico_controller import MedicoController


class MedicoView:
    def __init__(self):
        # janela
        self.root = tk.Tk()
        self.root.title("Médicos")
        self.root.geometry("820x460")
        self.root.resizable(False, False)

        # conexão + controller
        try:
            self.conexao = conectar()
            if not self.conexao:
                raise RuntimeError("Falha na conexão com o banco.")
            self.ctrl = MedicoController(self.conexao)
        except Exception as e:
            messagebox.showerror("Erro de conexão", str(e))
            return

        # --------- formulário ---------
        frm = tk.LabelFrame(self.root, text="Cadastro/edição", padx=8, pady=6)
        frm.place(x=10, y=10, width=800, height=160)

        tk.Label(frm, text="ID:").grid(row=0, column=0, sticky="w")
        self.ent_id = tk.Entry(frm, width=8, state="readonly")
        self.ent_id.grid(row=0, column=1, padx=(4, 16), sticky="w")

        tk.Label(frm, text="Nome:").grid(row=0, column=2, sticky="w")
        self.ent_nome = tk.Entry(frm, width=36)
        self.ent_nome.grid(row=0, column=3, padx=(4, 16), sticky="w")

        tk.Label(frm, text="CRM:").grid(row=1, column=2, sticky="w", pady=(6, 0))
        self.ent_crm = tk.Entry(frm, width=22)
        self.ent_crm.grid(row=1, column=3, padx=(4, 16), sticky="w", pady=(6, 0))

        tk.Label(frm, text="Especialidade:").grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.ent_espec = tk.Entry(frm, width=26)
        self.ent_espec.grid(row=1, column=1, padx=(4, 16), sticky="w", pady=(6, 0))

        self.var_ativo = tk.IntVar(value=1)
        tk.Checkbutton(frm, text="Ativo", variable=self.var_ativo).grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 0))

        tk.Button(frm, text="Novo", width=10, command=self.novo).grid(row=3, column=0, pady=10, sticky="w")
        tk.Button(frm, text="Salvar", width=12, command=self.salvar).grid(row=3, column=1, pady=10, sticky="w")
        tk.Button(frm, text="Excluir", width=10, command=self.excluir).grid(row=3, column=2, pady=10, sticky="w")

        # --------- busca ---------
        tk.Label(self.root, text="Buscar por nome:").place(x=12, y=180)
        self.ent_busca = tk.Entry(self.root, width=30)
        self.ent_busca.place(x=130, y=178)
        tk.Button(self.root, text="Buscar", command=self.buscar).place(x=340, y=175)
        tk.Button(self.root, text="Listar todos", command=self.carregar_tabela).place(x=410, y=175)

        # --------- tabela ---------
        cols = ("id", "nome", "crm", "especialidade", "ativo")
        self.tree = ttk.Treeview(self.root, columns=cols, show="headings", height=12)
        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("crm", text="CRM")
        self.tree.heading("especialidade", text="Especialidade")
        self.tree.heading("ativo", text="Ativo")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("nome", width=320)
        self.tree.column("crm", width=140)
        self.tree.column("especialidade", width=180)
        self.tree.column("ativo", width=70, anchor="center")

        self.tree.place(x=10, y=210, width=800, height=230)

        vsb = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        vsb.place(x=810, y=210, height=230)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.bind("<Double-1>", self.on_double_click)

        # inicial
        self.carregar_tabela()
        self.ent_nome.focus()
        self.root.mainloop()

    # --------- ações do formulário ---------
    def novo(self):
        self.ent_id.configure(state="normal"); self.ent_id.delete(0, tk.END); self.ent_id.configure(state="readonly")
        self.ent_nome.delete(0, tk.END)
        self.ent_crm.delete(0, tk.END)
        self.ent_espec.delete(0, tk.END)
        self.var_ativo.set(1)
        self.ent_nome.focus()

    def salvar(self):
        nome = (self.ent_nome.get() or "").strip()
        crm = (self.ent_crm.get() or "").strip() or None
        espec = (self.ent_espec.get() or "").strip() or None
        ativo = 1 if self.var_ativo.get() else 0

        try:
            id_text = self.ent_id.get().strip()
            if id_text:
                ok = self.ctrl.atualizar_dados(
                    id_medico=int(id_text),
                    nome=nome,
                    crm=crm,
                    especialidade=espec,
                    ativo=ativo
                )
                if ok:
                    messagebox.showinfo("Sucesso", "Médico atualizado.")
            else:
                new_id = self.ctrl.criar(nome, crm=crm, especialidade=espec, ativo=ativo)
                self.ent_id.configure(state="normal")
                self.ent_id.insert(0, str(new_id))
                self.ent_id.configure(state="readonly")
                messagebox.showinfo("Sucesso", f"Cadastrado com ID {new_id}.")
            self.carregar_tabela()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def excluir(self):
        id_text = self.ent_id.get().strip()
        if not id_text:
            messagebox.showwarning("Atenção", "Selecione um registro (duplo clique na tabela).")
            return
        if not messagebox.askyesno("Confirmar", "Excluir este médico?"):
            return
        try:
            ok = self.ctrl.excluir(int(id_text))
            if ok:
                messagebox.showinfo("OK", "Excluído.")
                self.novo()
                self.carregar_tabela()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    # --------- listagem/busca ---------
    def carregar_tabela(self):
        rows = self.ctrl.listar(apenas_ativos=False)
        self.preencher_tree(rows)

    def buscar(self):
        termo = (self.ent_busca.get() or "").strip().lower()
        if not termo:
            self.carregar_tabela(); return
        todos = self.ctrl.listar(apenas_ativos=False)
        filtrados = [r for r in todos if termo in (r.get("nome") or "").lower()]
        self.preencher_tree(filtrados)

    def preencher_tree(self, rows):
        self.tree.delete(*self.tree.get_children())
        for r in rows:
            self.tree.insert("", tk.END, values=(
                r.get("id_medico"),
                r.get("nome"),
                r.get("crm"),
                r.get("especialidade"),
                "Sim" if r.get("ativo") else "Não"
            ))

    # --------- eventos ---------
    def on_double_click(self, _event):
        item = self.tree.selection()
        if not item: return
        vals = self.tree.item(item[0], "values")
        self.ent_id.configure(state="normal")
        self.ent_id.delete(0, tk.END); self.ent_id.insert(0, vals[0]); self.ent_id.configure(state="readonly")
        self.ent_nome.delete(0, tk.END); self.ent_nome.insert(0, vals[1])
        self.ent_crm.delete(0, tk.END); self.ent_crm.insert(0, vals[2] if vals[2] != "None" else "")
        self.ent_espec.delete(0, tk.END); self.ent_espec.insert(0, vals[3] if vals[3] != "None" else "")
        self.var_ativo.set(1 if vals[4] == "Sim" else 0)


if __name__ == "__main__":
    MedicoView()
