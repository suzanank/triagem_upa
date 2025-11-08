import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime
from typing import Dict, List, Optional

from model.atendimento_model import AtendimentoRepository, Atendimento


class AtendimentoController:
    """
    Orquestra o fluxo de Atendimento:
    - cria atendimento por NOME do paciente (cria paciente se não existir)
    - gera senha automática (N### ou P###) via repository
    - lista/busca e atualiza status quando necessário
    """

    PRIORIDADES = {"NORMAL", "PRIORITARIO"}
    STATUS = {"AGUARDANDO", "TRIAGEM", "MEDICO", "FINALIZADO"}

    def __init__(self, conexao):
        self.con = conexao
        self.repo = AtendimentoRepository(conexao)

    # ----------------- helpers internos -----------------
    def _obter_ou_criar_paciente_por_nome(self, nome: str) -> int:
        """Retorna id_paciente pelo nome; cria se não existir."""
        nome = (nome or "").strip()
        if not nome:
            raise ValueError("Nome do paciente é obrigatório.")

        cur = self.con.cursor()
        try:
            cur.execute("SELECT id_paciente FROM paciente WHERE nome=%s LIMIT 1", (nome,))
            row = cur.fetchone()
            if row:
                return int(row[0])

            # cria paciente apenas com nome (data_nascimento pode ser preenchida na triagem)
            cur.execute("INSERT INTO paciente (nome) VALUES (%s)", (nome,))
            self.con.commit()
            return cur.lastrowid
        except Exception as e:
            self.con.rollback()
            raise RuntimeError(f"Erro ao obter/criar paciente: {e}") from e
        finally:
            cur.close()

    # ----------------- API pública -----------------
    def criar_atendimento_por_nome(self, nome_paciente: str, prioridade: str) -> Dict:
        """
        Cria um novo atendimento:
          1) resolve id_paciente pelo nome (criando se necessário)
          2) gera senha automática conforme prioridade
          3) insere em 'atendimento' com status 'AGUARDANDO'
        Retorna: {id_atendimento, id_paciente, senha, prioridade}
        """
        prio = (prioridade or "").upper()
        if prio not in self.PRIORIDADES:
            raise ValueError("Prioridade inválida. Use NORMAL ou PRIORITARIO.")

        id_paciente = self._obter_ou_criar_paciente_por_nome(nome_paciente)
        senha = self.repo.gerar_proxima_senha(prio)

        obj = Atendimento(
            id_paciente=id_paciente,
            senha=senha,
            prioridade=prio,
            data_chegada=datetime.now(),
            status="AGUARDANDO",
        )
        id_atendimento = self.repo.inserir(obj)

        return {
            "id_atendimento": id_atendimento,
            "id_paciente": id_paciente,
            "senha": senha,
            "prioridade": prio,
        }

    def listar(self) -> List[Dict]:
        return self.repo.listar_todos()

    def buscar_por_senha(self, senha: str) -> Optional[Dict]:
        senha = (senha or "").strip()
        if not senha:
            return None
        return self.repo.buscar_por_senha(senha)

    def atualizar_status(self, id_atendimento: int, novo_status: str) -> bool:
        ns = (novo_status or "").upper()
        if ns not in self.STATUS:
            raise ValueError(f"Status inválido. Use um de {self.STATUS}.")
        return self.repo.atualizar_status(id_atendimento, ns)

    def excluir(self, id_atendimento: int) -> bool:
        return self.repo.excluir(id_atendimento)
