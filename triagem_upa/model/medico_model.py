# triagem_upa/model/medico_model.py

class Medico:
    def __init__(self, id_medico=None, nome=None, crm=None, especialidade=None, ativo=1, created_at=None):
        self.id_medico = id_medico
        self.nome = nome
        self.crm = crm
        self.especialidade = especialidade
        self.ativo = ativo
        self.created_at = created_at

    def __str__(self):
        return f"[Médico {self.id_medico}] {self.nome} (CRM={self.crm or '—'}) esp={self.especialidade or '—'} ativo={self.ativo}"


class MedicoRepository:
    def __init__(self, conexao):
        self.con = conexao
        self._criar_tabela()

    def _criar_tabela(self):
        cur = self.con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS medico (
                id_medico     INT AUTO_INCREMENT PRIMARY KEY,
                nome          VARCHAR(120) NOT NULL,
                crm           VARCHAR(30)  NULL,
                especialidade VARCHAR(80)  NULL,
                ativo         TINYINT(1)   NOT NULL DEFAULT 1,
                created_at    TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT uk_medico_crm UNIQUE (crm)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        self.con.commit()
        cur.close()

    # -------------------------------
    # INSERIR
    # -------------------------------
    def inserir(self, med: Medico) -> int:
        sql = "INSERT INTO medico (nome, crm, especialidade, ativo) VALUES (%s, %s, %s, %s)"
        cur = self.con.cursor()
        try:
            cur.execute(sql, (med.nome, med.crm, med.especialidade, 1 if med.ativo else 0))
            self.con.commit()
            return cur.lastrowid
        except Exception as e:
            self.con.rollback()
            raise RuntimeError(f"Erro ao inserir médico: {e}") from e
        finally:
            cur.close()

    # -------------------------------
    # BUSCAS
    # -------------------------------
    def buscar_por_id(self, id_medico: int):
        sql = "SELECT * FROM medico WHERE id_medico = %s"
        cur = self.con.cursor(dictionary=True)
        cur.execute(sql, (id_medico,))
        row = cur.fetchone()
        cur.close()
        return row

    def buscar_por_nome(self, nome: str):
        sql = "SELECT * FROM medico WHERE nome = %s LIMIT 1"
        cur = self.con.cursor(dictionary=True)
        cur.execute(sql, (nome,))
        row = cur.fetchone()
        cur.close()
        return row

    def buscar_por_crm(self, crm: str):
        sql = "SELECT * FROM medico WHERE crm = %s LIMIT 1"
        cur = self.con.cursor(dictionary=True)
        cur.execute(sql, (crm,))
        row = cur.fetchone()
        cur.close()
        return row

    def listar(self, apenas_ativos: bool = False):
        if apenas_ativos:
            sql = "SELECT * FROM medico WHERE ativo = 1 ORDER BY nome"
        else:
            sql = "SELECT * FROM medico ORDER BY nome"
        cur = self.con.cursor(dictionary=True)
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        return rows

    # -------------------------------
    # ATUALIZAÇÕES
    # -------------------------------
    def atualizar_ativo(self, id_medico: int, ativo: int) -> bool:
        sql = "UPDATE medico SET ativo = %s WHERE id_medico = %s"
        cur = self.con.cursor()
        try:
            cur.execute(sql, (1 if ativo else 0, id_medico))
            self.con.commit()
            return cur.rowcount > 0
        except Exception as e:
            self.con.rollback()
            raise RuntimeError(f"Erro ao atualizar ativo: {e}") from e
        finally:
            cur.close()

    def atualizar_dados(self, id_medico: int, nome: str, crm: str | None, especialidade: str | None, ativo: int) -> bool:
        sql = "UPDATE medico SET nome=%s, crm=%s, especialidade=%s, ativo=%s WHERE id_medico=%s"
        cur = self.con.cursor()
        try:
            cur.execute(sql, (nome, crm, especialidade, 1 if ativo else 0, id_medico))
            self.con.commit()
            return cur.rowcount > 0
        except Exception as e:
            self.con.rollback()
            raise RuntimeError(f"Erro ao atualizar médico: {e}") from e
        finally:
            cur.close()

    # -------------------------------
    # EXCLUIR
    # -------------------------------
    def excluir(self, id_medico: int) -> bool:
        sql = "DELETE FROM medico WHERE id_medico = %s"
        cur = self.con.cursor()
        try:
            cur.execute(sql, (id_medico,))
            self.con.commit()
            return cur.rowcount > 0
        except Exception as e:
            self.con.rollback()
            raise RuntimeError(f"Erro ao excluir médico: {e}") from e
        finally:
            cur.close()

    # -------------------------------
    # UTILITÁRIO: obter ou criar
    # -------------------------------
    def obter_ou_criar(self, nome: str, crm: str | None = None, especialidade: str | None = None) -> int:
        """
        Se CRM for fornecido, tenta localizar pelo CRM (chave única).
        Caso contrário, tenta por nome. Se não encontrar, cria.
        """
        if crm:
            achado = self.buscar_por_crm(crm)
            if achado:
                return achado["id_medico"]

        if nome:
            achado = self.buscar_por_nome(nome)
            if achado:
                return achado["id_medico"]

        novo = Medico(nome=nome, crm=crm, especialidade=especialidade, ativo=1)
        return self.inserir(novo)
