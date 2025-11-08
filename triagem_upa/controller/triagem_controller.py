# triagem_upa/controller/triagem_controller.py

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from typing import Dict, Optional
from model.triagem_model import TriagemRepository, Triagem


class TriagemController:
    CLASSIF_VALIDAS = {"VERDE", "AMARELO", "VERMELHO"}

    def __init__(self, conexao):
        self.con = conexao
        self.repo = TriagemRepository(conexao)

    # -------- FILA: chamar próximo (prioriza PRIORITARIO) --------
    def chamar_proximo(self, prioridade: Optional[str] = None) -> Dict:
        params = []
        where = ["a.status = 'AGUARDANDO'"]
        if prioridade:
            pr = prioridade.upper()
            if pr not in {"PRIORITARIO", "NORMAL"}:
                raise ValueError("Prioridade inválida.")
            where.append("a.prioridade = %s")
            params.append(pr)

        sql = f"""
            SELECT a.id_atendimento, a.id_paciente, a.senha, a.prioridade, a.status, p.nome
            FROM atendimento a
            JOIN paciente p ON p.id_paciente = a.id_paciente
            WHERE {' AND '.join(where)}
            ORDER BY
              CASE a.prioridade WHEN 'PRIORITARIO' THEN 0 ELSE 1 END,
              a.data_chegada ASC
            LIMIT 1
        """
        cur = self.con.cursor(dictionary=True)
        cur.execute(sql, tuple(params))
        row = cur.fetchone()
        cur.close()

        if not row:
            raise ValueError("Não há atendimentos na fila.")

        # reserva: muda status para TRIAGEM
        upd = self.con.cursor()
        try:
            upd.execute("UPDATE atendimento SET status='TRIAGEM' WHERE id_atendimento=%s", (row["id_atendimento"],))
            self.con.commit()
        except Exception as e:
            self.con.rollback()
            raise RuntimeError(f"Falha ao reservar atendimento para triagem: {e}") from e
        finally:
            upd.close()

        row["status"] = "TRIAGEM"
        return row

    # -------- HEADERS / LOOKUPS --------
    def carregar_header_por_senha(self, senha: str) -> Dict:
        senha = (senha or "").strip()
        if not senha:
            raise ValueError("Senha é obrigatória.")
        row = self.repo.carregar_header_por_senha(senha)
        if not row:
            raise ValueError("Atendimento não encontrado para a senha informada.")
        return row

    def _buscar_id_atendimento_por_senha(self, senha: str) -> Dict:
        sql = "SELECT id_atendimento, id_paciente FROM atendimento WHERE senha=%s LIMIT 1"
        cur = self.con.cursor(dictionary=True)
        cur.execute(sql, (senha,))
        row = cur.fetchone()
        cur.close()
        if not row:
            raise ValueError("Atendimento não encontrado para a senha informada.")
        return row

    # -------- REGISTRAR TRIAGEM --------
    def registrar_triagem(
        self,
        senha: str,
        id_enfermeiro: int,
        classificacao: str,
        data_nascimento: str | None = None,
        pressao: str | None = None,
        temperatura: float | None = None,
        peso: float | None = None,
        sintomas: str | None = None
    ) -> Dict:
        if not id_enfermeiro or id_enfermeiro <= 0:
            raise ValueError("id_enfermeiro inválido.")

        cls = (classificacao or "").upper()
        if cls not in self.CLASSIF_VALIDAS:
            raise ValueError(f"Classificação inválida. Use {self.CLASSIF_VALIDAS}.")

        cab = self._buscar_id_atendimento_por_senha(senha)
        id_at = cab["id_atendimento"]
        id_pac = cab["id_paciente"]

        if data_nascimento:
            self.repo.atualizar_data_nascimento(id_pac, data_nascimento)

        tri = Triagem(
            id_atendimento=id_at,
            id_enfermeiro=id_enfermeiro,
            pressao=pressao,
            temperatura=temperatura,
            peso=peso,
            sintomas=sintomas,
            classificacao=cls
        )
        id_tri = self.repo.inserir(tri)

        # opcional: manter status em TRIAGEM (já setado ao chamar_proximo)

        header = self.carregar_header_por_senha(senha)
        return {
            "id_triagem": id_tri,
            "id_atendimento": id_at,
            "id_enfermeiro": id_enfermeiro,
            "nome": header["nome"],
            "senha": header["senha"],
            "classificacao": cls
        }
