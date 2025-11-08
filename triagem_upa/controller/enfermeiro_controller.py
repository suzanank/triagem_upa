# triagem_upa/controller/enfermeiro_controller.py

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from typing import Optional, List, Dict
from model.enfermeiro_model import Enfermeiro, EnfermeiroRepository


class EnfermeiroController:
    """
    Controller do Enfermeiro: centraliza criação, busca, listagem,
    atualização e exclusão. Usa EnfermeiroRepository por baixo.
    """

    def __init__(self, conexao):
        self.con = conexao
        self.repo = EnfermeiroRepository(conexao)  # <<< ESSENCIAL: repo é o repositório, não a conexão

    # ------------------ CRIAR ------------------
    def criar(self, nome: str, coren: Optional[str] = None, ativo: int = 1) -> int:
        nome = (nome or "").strip()
        if not nome:
            raise ValueError("Nome é obrigatório.")
        enf = Enfermeiro(nome=nome, coren=(coren or None), ativo=1 if ativo else 0)
        return self.repo.inserir(enf)

    # ------------------ LER ------------------
    def listar(self, apenas_ativos: bool = False) -> List[Dict]:
        return self.repo.listar(apenas_ativos=apenas_ativos)

    def buscar_por_id(self, id_enfermeiro: int) -> Optional[Dict]:
        return self.repo.buscar_por_id(id_enfermeiro)

    def buscar_por_nome(self, nome: str) -> Optional[Dict]:
        nome = (nome or "").strip()
        if not nome:
            raise ValueError("Nome é obrigatório.")
        return self.repo.buscar_por_nome(nome)

    # usado pela Triagem
    def obter_ou_criar_por_nome(self, nome: str) -> int:
        return self.repo.obter_ou_criar_por_nome(nome)

    # ------------------ ATUALIZAR ------------------
    def atualizar_dados(self, id_enfermeiro: int, nome: str, coren: Optional[str], ativo: int) -> bool:
        nome = (nome or "").strip()
        if not nome:
            raise ValueError("Nome é obrigatório.")
        sql = "UPDATE enfermeiro SET nome=%s, coren=%s, ativo=%s WHERE id_enfermeiro=%s"
        cur = self.con.cursor()
        try:
            cur.execute(sql, (nome, coren or None, 1 if ativo else 0, id_enfermeiro))
            self.con.commit()
            return cur.rowcount > 0
        except Exception as e:
            self.con.rollback()
            raise RuntimeError(f"Erro ao atualizar enfermeiro: {e}") from e
        finally:
            cur.close()

    def atualizar_ativo(self, id_enfermeiro: int, ativo: int) -> bool:
        return self.repo.atualizar_ativo(id_enfermeiro, ativo)

    # ------------------ EXCLUIR ------------------
    def excluir(self, id_enfermeiro: int) -> bool:
        return self.repo.excluir(id_enfermeiro)
