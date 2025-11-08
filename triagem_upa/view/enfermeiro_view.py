import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import tkinter as tk
from tkinter import ttk, messagebox

from model.dbconection import conectar
from controller.enfermeiro_controller import EnfermeiroController


class EnfermeiroView:
    def __init__(self):
        # conexão
        self.conn = conectar()
        if not self.conn:
            messagebox.showerror("Erro", "Não foi possível conectar ao banco.")
            return

        # controller (AGORA recebe a conexão, conforme seu controller final)
        self.ctrl = EnfermeiroController(self.conn)

        # janela
        self.janela = tk.Tk()
        self.janela.title("Cadastro de Enfermeiros")
        self.janela.geometry("720x520")
        self.janela.resizable(False, False)

        # título
        tk.Label(self.janela, text="Cadastro de Enfermeiros",
                 font=("Arial", 16, "bold")).pack(pady=10)

        # frame do formulário
        form = tk.Frame(self.janela)
        form.pack(pady=8)

        tk.Label(form, text="Nome:").grid(row=0, column=0, padx=6, pady=6, sticky="e")
        self.entry_nome = tk.Entry(form, width=42)
        self.entry_nome.grid(row=0, column=1, padx=6, pady=6, sticky="w")

        tk.Label(form, text="COREN:").grid(row=1, column=0, padx=6, pady=6, sticky="e")
        self.entry_coren = tk.Entry(form, width=42)
        self.entry_coren.grid(row=1, column=1, padx=6, pady=6, sticky="w")

        self.var_ativo = tk.IntVar(value=1)
        tk.Checkbutton(form, text="Ativo", variable=self.var_ativo).grid(row=2, column=1, sticky="w", padx=2, pady=2)

        # botões
        btns = tk.Frame(self.janela)
        btns.pack(pady=6)
        tk.Button(btns, text="Salvar", width=14, command=self.salvar).grid(row=0, column=0, padx=4)
        tk.Button(btns, text="Limpar", width=14, command=self.limpar_form).grid(row=0, column=1, padx=4)
        tk.Button(btns, text="Excluir Selecionado", width=18, command=self.excluir).grid(row=0, column=2, padx=4)

        # tabela
        cols = ("id", "nome", "coren", "ativo")
        self.tabela = ttk.Treeview(self.janela, columns=cols, show="headings", height=12, selectmode="browse")
        self.tabela.pack(fill="both", expand=True, padx=10, pady=8)

        self.tabela.heading("id", text="ID")
        self.tabela.heading("nome", text="Nome")
        self.tabela.heading("coren", text="COREN")
        self.tabela.heading("ativo", text="Ativo")

        self.tabela.column("id", width=60, anchor="center")
        self.tabela.column("nome", width=340)
        self.tabela.column("coren", width=160)
        self.tabela.column("ativo", width=60, anchor="center")

        # duplo clique = preencher formulário para edição
        self.tabela.bind("<Double-1>", self.preencher_form)

        # estado interno
        self.edit_id = None

        # carrega dados
        self.carregar_tabela()

        self.janela.mainloop()

    # -------------------------------
    # Carregar tabela
    # -------------------------------
    def carregar_tabela(self):
        for i in self.tabela.get_children():
            self.tabela.delete(i)

        rows = self.ctrl.listar(apenas_ativos=False)
        for r in rows:
            self.tabela.insert(
                "", "end",
                values=(r["id_enfermeiro"], r["nome"], r["coren"], r["ativo"])
            )

    # -------------------------------
    # Salvar (create/update)
    # -------------------------------
    def salvar(self):
        nome = self.entry_nome.get().strip()
        coren = self.entry_coren.get().strip()
        ativo = self.var_ativo.get()

        if not nome:
            messagebox.showwarning("Atenção", "O nome é obrigatório.")
            return

        # UPDATE
        if self.edit_id:
            try:
                ok = self.ctrl.atualizar_dados(self.edit_id, nome, coren or None, ativo)
                if ok:
                    messagebox.showinfo("Sucesso", "Enfermeiro atualizado!")
                else:
                    messagebox.showwarning("Aviso", "Nenhuma linha alterada.")
            except Exception as e:
                messagebox.showerror("Erro", str(e))
            self.edit_id = None
        else:
            # CREATE
            try:
                self.ctrl.criar(nome, coren or None, ativo)
                messagebox.showinfo("Sucesso", "Enfermeiro cadastrado!")
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        self.limpar_form()
        self.carregar_tabela()

    # -------------------------------
    # Preencher form (duplo clique)
    # -------------------------------
    def preencher_form(self, event):
        sel = self.tabela.selection()
        if not sel:
            return

        valores = self.tabela.item(sel, "values")
        self.edit_id = int(valores[0])

        self.entry_nome.delete(0, tk.END)
        self.entry_nome.insert(0, valores[1])

        self.entry_coren.delete(0, tk.END)
        self.entry_coren.insert(0, valores[2])

        self.var_ativo.set(int(valores[3]))

    # -------------------------------
    # Excluir
    # -------------------------------
    def excluir(self):
        sel = self.tabela.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione um enfermeiro para excluir.")
            return

        valores = self.tabela.item(sel, "values")
        enfermeiro_id = int(valores[0])
        nome = valores[1]

        if messagebox.askyesno("Confirmar exclusão",
                               f"Deseja realmente excluir o enfermeiro:\n\n{nome} (ID {enfermeiro_id})?"):
            try:
                if self.ctrl.excluir(enfermeiro_id):
                    messagebox.showinfo("OK", "Enfermeiro removido com sucesso.")
                    self.carregar_tabela()
                    self.limpar_form()
                else:
                    messagebox.showerror("Erro", "Não foi possível excluir.")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao excluir: {e}")

    # -------------------------------
    # Limpar form
    # -------------------------------
    def limpar_form(self):
        self.entry_nome.delete(0, tk.END)
        self.entry_coren.delete(0, tk.END)
        self.var_ativo.set(1)
        self.edit_id = None


if __name__ == "__main__":
    EnfermeiroView()
