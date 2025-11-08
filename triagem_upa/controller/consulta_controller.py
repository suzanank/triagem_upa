# triagem_upa/controller/consulta_controller.py
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from typing import Optional, Dict, List
from model.consulta_model import ConsultaRepository, Consulta


class ConsultaController:
    """
    Regras da Consulta:
    - Recebe id_atendimento e id_medico
    - Copia pressao, peso, classificacao e sintomas da ÚLTIMA triagem desse atendimento
    - Médico preenche apenas a CONDUTA
    - Pode chamar o próximo paciente triado conforme risco (VERMELHO > AMARELO > VERDE)
    - Ao reservar para consulta, muda status do atendimento para 'MEDICO'
    """

    def __init__(self, conexao):
        self.con = conexao
        self.repo = ConsultaRepository(conexao)

    # ------------- CHAMAR PRÓXIMO POR RISCO (triagem concluída) -------------
    def chamar_proximo_por_risco(self) -> Dict:
        """
        Seleciona o próximo atendimento já triado (status='TRIAGEM'),
        priorizando risco: VERMELHO > AMARELO > VERDE,
        desempate por data_triagem mais antiga.
        Reserva o atendimento mudando status para 'MEDICO'.
        Retorna cabeçalho completo (inclui senha e dados da última triagem).
        """
        sql = """
            SELECT 
                a.id_atendimento,
                a.senha,
                p.nome,
                t.classificacao,
                t.pressao,
                t.temperatura,
                t.peso,
                t.sintomas
            FROM atendimento a
            JOIN paciente p      ON p.id_paciente = a.id_paciente
            JOIN triagem  t      ON t.id_atendimento = a.id_atendimento
            WHERE a.status = 'TRIAGEM'
            ORDER BY 
                CASE t.classificacao 
                    WHEN 'VERMELHO' THEN 0
                    WHEN 'AMARELO'  THEN 1
                    ELSE 2
                END,
                t.data_triagem ASC
            LIMIT 1
        """
        cur = self.con.cursor(dictionary=True)
        cur.execute(sql)
        row = cur.fetchone()
        cur.close()

        if not row:
            raise ValueError("Não há pacientes triados aguardando consulta.")

        # Reserva: muda para MEDICO
        upd = self.con.cursor()
        try:
            upd.execute("UPDATE atendimento SET status='MEDICO' WHERE id_atendimento=%s", (row["id_atendimento"],))
            self.con.commit()
        except Exception as e:
            self.con.rollback()
            raise RuntimeError(f"Falha ao reservar atendimento para consulta: {e}") from e
        finally:
            upd.close()

        return row

    # ---------------- REGISTRAR CONSULTA ----------------
    def registrar_consulta(self, id_atendimento: int, id_medico: int, conduta: str) -> Dict:
        if not isinstance(id_atendimento, int) or id_atendimento <= 0:
            raise ValueError("id_atendimento inválido.")
        if not isinstance(id_medico, int) or id_medico <= 0:
            raise ValueError("id_medico inválido.")
        conduta = (conduta or "").strip()
        if not conduta:
            raise ValueError("A conduta médica é obrigatória.")

        # traz última triagem para esse atendimento
        tri = self.repo.obter_ultima_triagem(id_atendimento)
        pressao = tri["pressao"] if tri else None
        peso = tri["peso"] if tri else None
        classificacao = tri["classificacao"] if tri else None
        sintomas = tri["sintomas"] if tri else None

        c = Consulta(
            id_atendimento=id_atendimento,
            id_medico=id_medico,
            pressao=pressao,
            peso=peso,
            classificacao=classificacao,
            sintomas=sintomas,
            conduta=conduta
        )
        id_consulta = self.repo.inserir(c)

        # mantém/garante status como MEDICO (já foi reservado ao chamar_proximo_por_risco)
        self.repo.atualizar_status_atendimento(id_atendimento, "MEDICO")

        return {"id_consulta": id_consulta, "id_atendimento": id_atendimento, "id_medico": id_medico}

    # ---------------- CONSULTAS / BUSCAS ----------------
    def buscar_por_id(self, id_consulta: int) -> Optional[Dict]:
        return self.repo.buscar_por_id(id_consulta)

    def listar(self) -> List[Dict]:
        return self.repo.listar()

    def listar_por_atendimento(self, id_atendimento: int) -> List[Dict]:
        if not isinstance(id_atendimento, int) or id_atendimento <= 0:
            raise ValueError("id_atendimento inválido.")
        return self.repo.listar_por_atendimento(id_atendimento)

    # ---------------- OPCIONAL: finalizar atendimento ----------------
    def finalizar_atendimento(self, id_atendimento: int) -> bool:
        return self.repo.atualizar_status_atendimento(id_atendimento, "FINALIZADO")
