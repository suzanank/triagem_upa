import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import tkinter as tk
from tkinter import messagebox

from model.dbconection import conectar
from controller.atendimento_controller import AtendimentoController


class AtendimentoView:
    def __init__(self):
        # 1) cria a janela primeiro (se der erro de DB, a janela aparece e mostra a mensagem)
        self.root = tk.Tk()
        self.root.title("Atendimento")
        self.root.geometry("360x200")
        self.root.resizable(False, False)

        # UI básica
        tk.Label(self.root, text="nome:").grid(row=0, column=0, sticky="w", padx=10, pady=(12, 4))
        self.ent_nome = tk.Entry(self.root, width=30)
        self.ent_nome.grid(row=0, column=1, columnspan=2, sticky="w", padx=6, pady=(12, 4))

        tk.Label(self.root, text="atendimento:").grid(row=1, column=0, sticky="nw", padx=10, pady=(8, 0))
        self.var_prioridade = tk.StringVar(value="NORMAL")
        tk.Radiobutton(self.root, text="normal", variable=self.var_prioridade, value="NORMAL").grid(row=2, column=1, sticky="w")
        tk.Radiobutton(self.root, text="prioritário", variable=self.var_prioridade, value="PRIORITARIO").grid(row=3, column=1, sticky="w")

        self.btn_gerar = tk.Button(self.root, text="gerar atendimento", command=self.gerar_atendimento, state="disabled")
        self.btn_gerar.grid(row=4, column=1, sticky="w", pady=10)

        tk.Label(self.root, text="senha:").grid(row=5, column=0, sticky="w", padx=10)
        self.lbl_senha = tk.Label(self.root, text="—")
        self.lbl_senha.grid(row=5, column=1, sticky="w")

        self.ent_nome.bind("<Return>", lambda e: self.gerar_atendimento())
        self.ent_nome.focus_set()

        # 2) conecta no banco e cria o controller (com tratamento)
        self.conexao = None
        self.controller = None
        try:
            self.conexao = conectar()
            if not self.conexao:
                raise RuntimeError("Falha na conexão com o banco. Verifique usuário/senha/banco.")
            self.controller = AtendimentoController(self.conexao)
            self.btn_gerar.configure(state="normal")  # habilita o botão só após conexão ok
        except Exception as e:
            messagebox.showerror("Erro de conexão", str(e))

        self.root.mainloop()

    def gerar_atendimento(self):
        if not self.controller:
            messagebox.showwarning("Atenção", "Sem conexão com o banco.")
            return

        nome = (self.ent_nome.get() or "").strip()
        if not nome:
            messagebox.showwarning("Atenção", "Informe o nome do paciente.")
            self.ent_nome.focus_set()
            return

        prioridade = self.var_prioridade.get()
        try:
            res = self.controller.criar_atendimento_por_nome(nome, prioridade)
            self.lbl_senha.config(text=res["senha"])
            messagebox.showinfo("Atendimento criado",
                                f"Paciente: {nome}\nPrioridade: {res['prioridade']}\nSenha: {res['senha']}")
            self.ent_nome.delete(0, tk.END)
            self.ent_nome.focus_set()
        except Exception as e:
            messagebox.showerror("Erro", str(e))


if __name__ == "__main__":
    AtendimentoView()
