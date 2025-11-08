# triagem_upa/controller/paciente_controller.py
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from typing import Optional, List, Dict
from model.paciente_model import Paciente, PacienteRepository


class PacienteController:
    def __init__(self, conexao):
        self.con = conexao
        self.repo = PacienteRepository(conexao)

    # criar
    def criar(self, nome: str, cpf: Optional[str] = None, data_nascimento: Optional[str] = None, telefone: Optional[str] = None) -> int:
        nome = (nome or "").strip()
        if not nome:
            raise ValueError("Nome do paciente é obrigatório.")
        pac = Paciente(nome=nome, cpf=(cpf or None), data_nascimento=(data_nascimento or None), telefone=(telefone or None))
        return self.repo.inserir(pac)

    # ler
    def listar(self) -> List[Dict]:
        return self.repo.listar()

    def buscar_por_id(self, id_paciente: int) -> Optional[Dict]:
        return self.repo.buscar_por_id(id_paciente)

    def buscar_por_nome(self, nome: str) -> Optional[Dict]:
        nome = (nome or "").strip()
        if not nome:
            raise ValueError("Nome é obrigatório.")
        return self.repo.buscar_por_nome(nome)

    # atualizar
    def atualizar_dados(self, id_paciente: int, nome: str, cpf: Optional[str], data_nascimento: Optional[str], telefone: Optional[str]) -> bool:
        nome = (nome or "").strip()
        if not nome:
            raise ValueError("Nome do paciente é obrigatório.")
        return self.repo.atualizar_dados(id_paciente, nome, cpf or None, data_nascimento or None, telefone or None)

    # excluir
    def excluir(self, id_paciente: int) -> bool:
        return self.repo.excluir(id_paciente)

    # utilitário
    def obter_ou_criar_por_nome(self, nome: str) -> int:
        return self.repo.obter_ou_criar_por_nome(nome)
