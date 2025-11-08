# triagem_upa/view/consulta_view.py
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import tkinter as tk
from tkinter import messagebox

from model.dbconection import conectar
from controller.consulta_controller import ConsultaController
from controller.medico_controller import MedicoController
from controller.triagem_controller import TriagemController


class ConsultaView:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Consulta Médica")
        self.root.geometry("600x660")
        self.root.resizable(False, False)

        # Conexões
        try:
            self.con = conectar()
            if not self.con:
                raise RuntimeError("Falha ao conectar ao banco.")
            self.consulta_ctrl = ConsultaController(self.con)
            self.med_ctrl = MedicoController(self.con)
            self.tri_ctrl = TriagemController(self.con)
        except Exception as e:
            messagebox.showerror("Erro", str(e))
            return

        # ==== Header: chamar próximo por risco ====
        tk.Button(self.root, text="Chamar próximo (por risco)", command=self.chamar_proximo)\
            .grid(row=0, column=0, padx=12, pady=12, sticky="w")

        # Fallback: carregar por senha manual
        tk.Label(self.root, text="ou carregue por senha:").grid(row=0, column=1, sticky="e")
        self.ent_senha = tk.Entry(self.root, width=12)
        self.ent_senha.grid(row=0, column=2, sticky="w")
        tk.Button(self.root, text="carregar", command=self.carregar_por_senha)\
            .grid(row=0, column=3, padx=8)

        # ==== Labels com dados ====
        row = 1
        tk.Label(self.root, text="senha:").grid(row=row, column=0, sticky="w", padx=12)
        self.lbl_senha = tk.Label(self.root, text="—"); self.lbl_senha.grid(row=row, column=1, sticky="w")

        row += 1
        tk.Label(self.root, text="paciente:").grid(row=row, column=0, sticky="w", padx=12)
        self.lbl_nome = tk.Label(self.root, text="—"); self.lbl_nome.grid(row=row, column=1, sticky="w")

        row += 1
        tk.Label(self.root, text="classificação:").grid(row=row, column=0, sticky="w", padx=12)
        self.lbl_classif = tk.Label(self.root, text="—"); self.lbl_classif.grid(row=row, column=1, sticky="w")

        row += 1
        tk.Label(self.root, text="pressão:").grid(row=row, column=0, sticky="w", padx=12)
        self.lbl_pressao = tk.Label(self.root, text="—"); self.lbl_pressao.grid(row=row, column=1, sticky="w")

        row += 1
        tk.Label(self.root, text="temperatura:").grid(row=row, column=0, sticky="w", padx=12)
        self.lbl_temp = tk.Label(self.root, text="—"); self.lbl_temp.grid(row=row, column=1, sticky="w")

        row += 1
        tk.Label(self.root, text="peso:").grid(row=row, column=0, sticky="w", padx=12)
        self.lbl_peso = tk.Label(self.root, text="—"); self.lbl_peso.grid(row=row, column=1, sticky="w")

        row += 1
        tk.Label(self.root, text="sintomas:").grid(row=row, column=0, sticky="nw", padx=12)
        self.lbl_sintomas = tk.Label(self.root, text="—", justify="left", wraplength=360)
        self.lbl_sintomas.grid(row=row, column=1, columnspan=3, sticky="w")

        # Médico ativo automático
        row += 1
        tk.Label(self.root, text="médico responsável:").grid(row=row, column=0, sticky="w", padx=12, pady=(16, 4))
        self.lbl_medico = tk.Label(self.root, text="—")
        self.lbl_medico.grid(row=row, column=1, columnspan=3, sticky="w", pady=(16, 4))
        self.medico_id = None

        # Conduta
        row += 1
        tk.Label(self.root, text="conduta médica:").grid(row=row, column=0, sticky="nw", padx=12)
        self.txt_conduta = tk.Text(self.root, width=50, height=10)
        self.txt_conduta.grid(row=row, column=1, columnspan=3, pady=10, sticky="w")

        # Ações
        row += 1
        tk.Button(self.root, text="registrar consulta", command=self.salvar)\
            .grid(row=row, column=1, sticky="w", pady=12)

        # estado interno
        self.id_atendimento_carregado = None

        self.root.mainloop()

    # ===================== Fluxos =====================

    def chamar_proximo(self):
        """Chama o próximo paciente já triado conforme risco e preenche tudo."""
        try:
            row = self.consulta_ctrl.chamar_proximo_por_risco()
            # Preenche cabeçalho com dados trazidos
            self.id_atendimento_carregado = row["id_atendimento"]
            self.lbl_senha.config(text=row["senha"])
            self.lbl_nome.config(text=row["nome"])
            self.lbl_classif.config(text=row["classificacao"] or "—")
            self.lbl_pressao.config(text=row["pressao"] or "—")
            self.lbl_temp.config(text=(str(row["temperatura"]) if row["temperatura"] is not None else "—"))
            self.lbl_peso.config(text=(str(row["peso"]) if row["peso"] is not None else "—"))
            self.lbl_sintomas.config(text=row["sintomas"] or "—")

            self._carregar_medico_ativo()
            messagebox.showinfo("OK", f"Chamado: {row['senha']} ({row['classificacao']})")
        except Exception as e:
            messagebox.showwarning("Aviso", str(e))

    def carregar_por_senha(self):
        """Fallback: carrega manualmente por senha já triada (status TRIAGEM)."""
        senha = (self.ent_senha.get() or "").strip()
        if not senha:
            messagebox.showwarning("Atenção", "Informe uma senha.")
            return
        try:
            # Busca cabeçalho geral
            cab = self.tri_ctrl.carregar_header_por_senha(senha)  # contém id_atendimento, nome etc.
            self.id_atendimento_carregado = cab["id_atendimento"]
            self.lbl_senha.config(text=cab["senha"])
            self.lbl_nome.config(text=cab["nome"])

            # Carrega últimos detalhes da triagem desse atendimento
            tri = self._carregar_detalhes_triagem(self.id_atendimento_carregado)
            if not tri:
                raise ValueError("Não há triagem registrada para essa senha.")

            self.lbl_classif.config(text=tri["classificacao"] or "—")
            self.lbl_pressao.config(text=tri["pressao"] or "—")
            self.lbl_temp.config(text=(str(tri["temperatura"]) if tri["temperatura"] is not None else "—"))
            self.lbl_peso.config(text=(str(tri["peso"]) if tri["peso"] is not None else "—"))
            self.lbl_sintomas.config(text=tri["sintomas"] or "—")

            # Reserva para consulta
            self.consulta_ctrl.repo.atualizar_status_atendimento(self.id_atendimento_carregado, "MEDICO")

            self._carregar_medico_ativo()
            messagebox.showinfo("OK", f"Dados carregados para senha {senha}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _carregar_detalhes_triagem(self, id_atendimento):
        sql = """
            SELECT pressao, temperatura, peso, sintomas, classificacao
            FROM triagem
            WHERE id_atendimento = %s
            ORDER BY data_triagem DESC
            LIMIT 1
        """
        cur = self.con.cursor(dictionary=True)
        cur.execute(sql, (id_atendimento,))
        row = cur.fetchone()
        cur.close()
        return row

    def _carregar_medico_ativo(self):
        # ATENÇÃO: método listar do MedicoController usa parametro 'apenas_ativos'
        lista = self.med_ctrl.listar(apenas_ativos=True)
        if not lista:
            messagebox.showwarning("Aviso", "Nenhum médico ativo encontrado!")
            self.lbl_medico.config(text="—")
            self.medico_id = None
            return
        med = lista[0]
        self.medico_id = med["id_medico"]
        self.lbl_medico.config(text=f"{med['nome']} ({med.get('especialidade') or ''})")

    def salvar(self):
        if not self.id_atendimento_carregado:
            messagebox.showwarning("Atenção", "Chame um paciente ou carregue por senha primeiro.")
            return
        if not self.medico_id:
            messagebox.showwarning("Atenção", "Nenhum médico ativo disponível.")
            return

        conduta = (self.txt_conduta.get("1.0", tk.END) or "").strip()
        if not conduta:
            messagebox.showwarning("Atenção", "A conduta médica é obrigatória.")
            return

        try:
            res = self.consulta_ctrl.registrar_consulta(
                id_atendimento=self.id_atendimento_carregado,
                id_medico=self.medico_id,
                conduta=conduta
            )
            messagebox.showinfo(
                "Consulta registrada",
                f"Consulta ID: {res['id_consulta']}\nMédico: {self.lbl_medico.cget('text')}"
            )
            self._resetar()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _resetar(self):
        self.ent_senha.delete(0, tk.END)
        self.lbl_senha.config(text="—")
        self.lbl_nome.config(text="—")
        self.lbl_classif.config(text="—")
        self.lbl_pressao.config(text="—")
        self.lbl_temp.config(text="—")
        self.lbl_peso.config(text="—")
        self.lbl_sintomas.config(text="—")
        self.lbl_medico.config(text="—")
        self.txt_conduta.delete("1.0", tk.END)
        self.id_atendimento_carregado = None


if __name__ == "__main__":
    ConsultaView()
