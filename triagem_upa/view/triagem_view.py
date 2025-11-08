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
        self.root = tk.Tk()
        self.root.title("Triagem")
        self.root.geometry("540x590")
        self.root.resizable(False, False)

        # conexão/controllers
        try:
            self.con = conectar()
            if not self.con:
                raise RuntimeError("Falha na conexão com o banco.")
            self.tri_ctl = TriagemController(self.con)
            self.enf_ctl = EnfermeiroController(self.con)
        except Exception as e:
            messagebox.showerror("Erro de conexão", str(e))
            return

        # header
        tk.Button(self.root, text="Chamar próximo", command=self.chamar_proximo)\
            .grid(row=0, column=0, padx=12, pady=12, sticky="w")

        tk.Label(self.root, text="paciente:").grid(row=1, column=0, padx=12, sticky="w")
        self.lbl_nome = tk.Label(self.root, text="—"); self.lbl_nome.grid(row=1, column=1, sticky="w")

        tk.Label(self.root, text="tipo:").grid(row=2, column=0, padx=12, sticky="w")
        self.lbl_tipo = tk.Label(self.root, text="—"); self.lbl_tipo.grid(row=2, column=1, sticky="w")

        tk.Label(self.root, text="senha:").grid(row=3, column=0, padx=12, sticky="w")
        self.lbl_senha = tk.Label(self.root, text="—"); self.lbl_senha.grid(row=3, column=1, sticky="w")
        self.senha_atual = None

        # enfermeiro automático
        tk.Label(self.root, text="enfermeiro responsável:").grid(row=4, column=0, padx=12, pady=(12, 4), sticky="w")
        self.lbl_enf = tk.Label(self.root, text="—")
        self.lbl_enf.grid(row=4, column=1, sticky="w", pady=(12, 4))
        self.enfermeiro_ativo_id = None

        # entradas
        tk.Label(self.root, text="data nascimento (AAAA-MM-DD):").grid(row=5, column=0, padx=12, sticky="w")
        self.ent_nasc = tk.Entry(self.root, width=18); self.ent_nasc.grid(row=5, column=1, sticky="w")

        tk.Label(self.root, text="pressão:").grid(row=6, column=0, padx=12, sticky="w")
        self.ent_pressao = tk.Entry(self.root, width=18); self.ent_pressao.grid(row=6, column=1, sticky="w")

        tk.Label(self.root, text="temperatura (°C):").grid(row=7, column=0, padx=12, sticky="w")
        self.ent_temp = tk.Entry(self.root, width=18); self.ent_temp.grid(row=7, column=1, sticky="w")

        tk.Label(self.root, text="peso (kg):").grid(row=8, column=0, padx=12, sticky="w")
        self.ent_peso = tk.Entry(self.root, width=18); self.ent_peso.grid(row=8, column=1, sticky="w")

        tk.Label(self.root, text="sintomas:").grid(row=9, column=0, padx=12, sticky="nw")
        self.txt_sintomas = tk.Text(self.root, width=36, height=6)
        self.txt_sintomas.grid(row=9, column=1, columnspan=2, padx=6, pady=6, sticky="w")

        tk.Label(self.root, text="classificação:").grid(row=10, column=0, padx=12, pady=(8, 0), sticky="w")
        self.var_classif = tk.StringVar(value="VERDE")
        tk.Radiobutton(self.root, text="verde", value="VERDE", variable=self.var_classif).grid(row=10, column=1, sticky="w")
        tk.Radiobutton(self.root, text="amarelo", value="AMARELO", variable=self.var_classif).grid(row=11, column=1, sticky="w")
        tk.Radiobutton(self.root, text="vermelho", value="VERMELHO", variable=self.var_classif).grid(row=12, column=1, sticky="w")

        self.btn_salvar = tk.Button(self.root, text="registrar triagem", command=self.salvar, state="disabled")
        self.btn_salvar.grid(row=13, column=1, pady=16, sticky="w")

        # carregar enfermeiro ativo
        self._carregar_enfermeiro_ativo()

        self.root.mainloop()

    # --- helpers ---
    def _carregar_enfermeiro_ativo(self):
        try:
            ativos = self.enf_ctl.listar(apenas_ativos=True)
            if not ativos:
                self.enfermeiro_ativo_id = None
                self.lbl_enf.config(text="— (nenhum ativo)")
                messagebox.showwarning("Aviso", "Nenhum enfermeiro ATIVO encontrado.")
                return
            enf = ativos[0]  # primeiro ativo (podemos fazer rodízio se quiser)
            self.enfermeiro_ativo_id = enf["id_enfermeiro"]
            self.lbl_enf.config(text=enf["nome"])
        except Exception as e:
            self.enfermeiro_ativo_id = None
            self.lbl_enf.config(text="—")
            messagebox.showerror("Erro", f"Erro ao carregar enfermeiro ativo: {e}")

    def chamar_proximo(self):
        try:
            dados = self.tri_ctl.chamar_proximo()
            self.lbl_nome.config(text=dados["nome"])
            self.lbl_tipo.config(text=dados["prioridade"])
            self.lbl_senha.config(text=dados["senha"])
            self.senha_atual = dados["senha"]
            self.btn_salvar.configure(state="normal")
            # recarrega enfermeiro ativo (caso tenha mudado)
            self._carregar_enfermeiro_ativo()
            messagebox.showinfo("OK", f"Chamado: {dados['senha']} ({dados['prioridade']})")
        except Exception as e:
            messagebox.showwarning("Fila vazia", str(e))

    def salvar(self):
        if not self.senha_atual:
            messagebox.showwarning("Atenção", "Chame um atendimento primeiro.")
            return
        if not self.enfermeiro_ativo_id:
            messagebox.showwarning("Atenção", "Nenhum enfermeiro ATIVO disponível.")
            return

        data_nasc = (self.ent_nasc.get() or "").strip() or None
        pressao = (self.ent_pressao.get() or "").strip() or None

        tmp = (self.ent_temp.get() or "").strip()
        temperatura = None
        if tmp:
            try:
                temperatura = float(tmp.replace(",", "."))
            except ValueError:
                messagebox.showwarning("Atenção", "Temperatura inválida (ex.: 37.5).")
                self.ent_temp.focus_set(); return

        p = (self.ent_peso.get() or "").strip()
        peso = None
        if p:
            try:
                peso = float(p.replace(",", "."))
            except ValueError:
                messagebox.showwarning("Atenção", "Peso inválido (ex.: 72.5).")
                self.ent_peso.focus_set(); return

        sintomas = (self.txt_sintomas.get("1.0", tk.END) or "").strip() or None
        classif = self.var_classif.get()

        try:
            res = self.tri_ctl.registrar_triagem(
                senha=self.senha_atual,
                id_enfermeiro=self.enfermeiro_ativo_id,
                classificacao=classif,
                data_nascimento=data_nasc,
                pressao=pressao,
                temperatura=temperatura,
                peso=peso,
                sintomas=sintomas
            )
            messagebox.showinfo(
                "Triagem registrada",
                f"Paciente: {res['nome']}\nClassificação: {res['classificacao']}\nID Triagem: {res['id_triagem']}"
            )
            self._resetar_form()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _resetar_form(self):
        self.lbl_nome.config(text="—")
        self.lbl_tipo.config(text="—")
        self.lbl_senha.config(text="—")
        self.ent_nasc.delete(0, tk.END)
        self.ent_pressao.delete(0, tk.END)
        self.ent_temp.delete(0, tk.END)
        self.ent_peso.delete(0, tk.END)
        self.txt_sintomas.delete("1.0", tk.END)
        self.var_classif.set("VERDE")
        self.senha_atual = None
        self.btn_salvar.configure(state="disabled")


if __name__ == "__main__":
    TriagemView()
