# triagem_upa/view/triagem_view.py
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import tkinter as tk
from tkinter import messagebox

from model.dbconection import conectar
from controller.triagem_controller import TriagemController
from controller.enfermeiro_controller import EnfermeiroController


class TriagemView:
    def __init__(self):
        # ===== janela =====
        self.root = tk.Tk()
        self.root.title("Triagem")
        self.root.geometry("520x560")
        self.root.resizable(False, False)

        # ===== conexões/controllers =====
        self.con = None
        self.tri_ctl = None
        self.enf_ctl = None
        try:
            self.con = conectar()
            if not self.con:
                raise RuntimeError("Falha na conexão com o banco (verifique host/usuário/senha/banco).")
            self.tri_ctl = TriagemController(self.con)
            self.enf_ctl = EnfermeiroController(self.con)
        except Exception as e:
            messagebox.showerror("Erro de conexão", str(e))

        # ===== header (preenchido ao chamar próximo) =====
        tk.Button(self.root, text="Chamar próximo", command=self.chamar_proximo)\
            .grid(row=0, column=0, padx=12, pady=12, sticky="w")

        tk.Label(self.root, text="paciente:").grid(row=1, column=0, padx=12, sticky="w")
        self.lbl_nome = tk.Label(self.root, text="—"); self.lbl_nome.grid(row=1, column=1, sticky="w")

        tk.Label(self.root, text="tipo:").grid(row=2, column=0, padx=12, sticky="w")
        self.lbl_tipo = tk.Label(self.root, text="—"); self.lbl_tipo.grid(row=2, column=1, sticky="w")

        tk.Label(self.root, text="senha:").grid(row=3, column=0, padx=12, sticky="w")
        self.lbl_senha = tk.Label(self.root, text="—"); self.lbl_senha.grid(row=3, column=1, sticky="w")

        # guarda a senha atual para salvar triagem
        self.senha_atual = None

        # ===== enfermeiro (AUTOMÁTICO) =====
        tk.Label(self.root, text="enfermeiro responsável:").grid(row=4, column=0, padx=12, pady=(12, 4), sticky="w")
        self.lbl_enf = tk.Label(self.root, text="—")
        self.lbl_enf.grid(row=4, column=1, sticky="w", pady=(12, 4))
        self.enfermeiro_ativo_id = None

        # ===== entradas da triagem =====
        tk.Label(self.root, text="data nascimento (AAAA-MM-DD):").grid(row=5, column=0, padx=12, sticky="w")
        self.ent_nasc = tk.Entry(self.root, width=18); self.ent_nasc.grid(row=5, column=1, sticky="w")

        tk.Label(self.root, text="pressão:").grid(row=6, column=0, padx=12, sticky="w")
        self.ent_pressao = tk.Entry(self.root, width=18); self.ent_pressao.grid(row=6, column=1, sticky="w")

        tk.Label(self.root, text="peso (kg):").grid(row=7, column=0, padx=12, sticky="w")
        self.ent_peso = tk.Entry(self.root, width=18); self.ent_peso.grid(row=7, column=1, sticky="w")

        tk.Label(self.root, text="sintomas:").grid(row=8, column=0, padx=12, sticky="nw")
        self.txt_sintomas = tk.Text(self.root, width=36, height=6)
        self.txt_sintomas.grid(row=8, column=1, columnspan=2, padx=6, pady=6, sticky="w")

        tk.Label(self.root, text="classificação:").grid(row=9, column=0, padx=12, pady=(8, 0), sticky="w")
        self.var_classif = tk.StringVar(value="VERDE")
        tk.Radiobutton(self.root, text="verde", value="VERDE", variable=self.var_classif).grid(row=9, column=1, sticky="w")
        tk.Radiobutton(self.root, text="amarelo", value="AMARELO", variable=self.var_classif).grid(row=10, column=1, sticky="w")
        tk.Radiobutton(self.root, text="vermelho", value="VERMELHO", variable=self.var_classif).grid(row=11, column=1, sticky="w")

        self.btn_salvar = tk.Button(self.root, text="registrar triagem", command=self.salvar, state="disabled")
        self.btn_salvar.grid(row=12, column=1, pady=16, sticky="w")

        # carrega automaticamente o enfermeiro ativo
        self._carregar_enfermeiro_ativo()

        self.root.mainloop()

    # ---------- carrega o enfermeiro ativo ----------
    def _carregar_enfermeiro_ativo(self):
        if not self.enf_ctl:
            return
        try:
            ativos = self.enf_ctl.listar(apenas_ativos=True)
            if not ativos:
                self.enfermeiro_ativo_id = None
                self.lbl_enf.config(text="— (nenhum ativo)")
                messagebox.showwarning("Aviso", "Nenhum enfermeiro ATIVO encontrado.")
                return
            # pega o primeiro ativo (podemos implementar rodízio se quiser)
            enf = ativos[0]
            self.enfermeiro_ativo_id = enf["id_enfermeiro"]
            self.lbl_enf.config(text=enf["nome"])
        except Exception as e:
            self.enfermeiro_ativo_id = None
            self.lbl_enf.config(text="—")
            messagebox.showerror("Erro", f"Erro ao carregar enfermeiro ativo: {e}")

    # ---------- chamar próximo da fila ----------
    def chamar_proximo(self):
        if not self.tri_ctl:
            messagebox.showerror("Erro", "Sem conexão com o banco.")
            return
        try:
            dados = self.tri_ctl.chamar_proximo()  # prioriza PRIORITARIO e marca TRIAGEM
            self.lbl_nome.config(text=dados["nome"])
            self.lbl_tipo.config(text=dados["prioridade"])
            self.lbl_senha.config(text=dados["senha"])
            self.senha_atual = dados["senha"]
            self.btn_salvar.configure(state="normal")

            # sempre recarrega o enfermeiro ativo (caso tenha mudado)
            self._carregar_enfermeiro_ativo()

            messagebox.showinfo("OK", f"Chamado: {dados['senha']} ({dados['prioridade']})")
        except Exception as e:
            messagebox.showwarning("Fila vazia", str(e))

    # ---------- salvar triagem ----------
    def salvar(self):
        if not self.senha_atual:
            messagebox.showwarning("Atenção", "Chame um atendimento primeiro.")
            return

        if not self.enfermeiro_ativo_id:
            messagebox.showwarning("Atenção", "Nenhum enfermeiro ATIVO disponível.")
            return

        data_nasc = (self.ent_nasc.get() or "").strip() or None
        pressao = (self.ent_pressao.get() or "").strip() or None

        peso_val = None
        peso_str = (self.ent_peso.get() or "").strip()
        if peso_str:
            try:
                peso_val = float(peso_str.replace(",", "."))
            except ValueError:
                messagebox.showwarning("Atenção", "Peso inválido. Use número (ex.: 72.5).")
                self.ent_peso.focus_set()
                return

        sintomas = (self.txt_sintomas.get("1.0", tk.END) or "").strip() or None
        classif = self.var_classif.get()

        try:
            res = self.tri_ctl.registrar_triagem(
                senha=self.senha_atual,
                id_enfermeiro=self.enfermeiro_ativo_id,
                classificacao=classif,
                data_nascimento=data_nasc,
                pressao=pressao,
                peso=peso_val,
                sintomas=sintomas
            )
            messagebox.showinfo(
                "Triagem registrada",
                f"Paciente: {res['nome']}\nClassificação: {res['classificacao']}\nID Triagem: {res['id_triagem']}"
            )
            self.reset_form()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def reset_form(self):
        self.lbl_nome.config(text="—")
        self.lbl_tipo.config(text="—")
        self.lbl_senha.config(text="—")
        self.ent_nasc.delete(0, tk.END)
        self.ent_pressao.delete(0, tk.END)
        self.ent_peso.delete(0, tk.END)
        self.txt_sintomas.delete("1.0", tk.END)
        self.var_classif.set("VERDE")
        self.senha_atual = None
        self.btn_salvar.configure(state="disabled")
        # mantém o enfermeiro ativo atual exibido


if __name__ == "__main__":
    TriagemView()