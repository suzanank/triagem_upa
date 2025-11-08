# triagem_upa/controller/medico_controller.py

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from typing import Optional, List, Dict
from model.medico_model import Medico, MedicoRepository


class MedicoController:
    """
    Controller do Médico: criação, buscas, listagem, atualização e exclusão.
    Usa MedicoRepository internamente (recebe a conexão no __init__).
    """

    def __init__(self, conexao):
        self.con = conexao
        self.repo = MedicoRepository(conexao)

    # ------------------ CRIAR ------------------
    def criar(self, nome: str, crm: Optional[str] = None,
              especialidade: Optional[str] = None, ativo: int = 1) -> int:
        nome = (nome or "").strip()
        if not nome:
            raise ValueError("Nome do médico é obrigatório.")
        med = Medico(
            nome=nome,
            crm=(crm or None),
            especialidade=(especialidade or None),
            ativo=1 if ativo else 0
        )
        return self.repo.inserir(med)

    # ------------------ LER ------------------
    def listar(self, apenas_ativos: bool = False) -> List[Dict]:
        return self.repo.listar(apenas_ativos=apenas_ativos)

    def buscar_por_id(self, id_medico: int) -> Optional[Dict]:
        return self.repo.buscar_por_id(id_medico)

    def buscar_por_nome(self, nome: str) -> Optional[Dict]:
        nome = (nome or "").strip()
        if not nome:
            raise ValueError("Nome é obrigatório.")
        return self.repo.buscar_por_nome(nome)

    def buscar_por_crm(self, crm: str) -> Optional[Dict]:
        crm = (crm or "").strip()
        if not crm:
            raise ValueError("CRM é obrigatório.")
        return self.repo.buscar_por_crm(crm)

    # usado pela Consulta (ou cadastros rápidos)
    def obter_ou_criar(self, nome: str, crm: Optional[str] = None,
                       especialidade: Optional[str] = None) -> int:
        nome = (nome or "").strip()
        if not nome and not crm:
            raise ValueError("Informe ao menos nome ou CRM.")
        return self.repo.obter_ou_criar(nome=nome, crm=crm, especialidade=especialidade)

    # ------------------ ATUALIZAR ------------------
    def atualizar_dados(self, id_medico: int, nome: str,
                        crm: Optional[str], especialidade: Optional[str],
                        ativo: int) -> bool:
        nome = (nome or "").strip()
        if not nome:
            raise ValueError("Nome do médico é obrigatório.")
        return self.repo.atualizar_dados(
            id_medico=id_medico,
            nome=nome,
            crm=(crm or None),
            especialidade=(especialidade or None),
            ativo=1 if ativo else 0
        )

    def atualizar_ativo(self, id_medico: int, ativo: int) -> bool:
        if ativo not in (0, 1):
            raise ValueError("ativo deve ser 0 ou 1")
        return self.repo.atualizar_ativo(id_medico, ativo)

    # ------------------ EXCLUIR ------------------
    def excluir(self, id_medico: int) -> bool:
        if not isinstance(id_medico, int) or id_medico <= 0:
            raise ValueError("ID inválido.")
        return self.repo.excluir(id_medico)
