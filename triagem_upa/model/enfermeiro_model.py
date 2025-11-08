# triagem_upa/model/enfermeiro_model.py

class Enfermeiro:
    def __init__(self, id_enfermeiro=None, nome=None, coren=None, ativo=1, created_at=None):
        self.id_enfermeiro = id_enfermeiro
        self.nome = nome
        self.coren = coren
        self.ativo = ativo
        self.created_at = created_at

    def __str__(self):
        return f"[Enfermeiro {self.id_enfermeiro}] {self.nome} (COREN={self.coren}) ativo={self.ativo}"
        

class EnfermeiroRepository:
    def __init__(self, conexao):
        self.con = conexao
        self._criar_tabela()

    def _criar_tabela(self):
        cur = self.con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS enfermeiro (
                id_enfermeiro INT AUTO_INCREMENT PRIMARY KEY,
                nome          VARCHAR(120) NOT NULL,
                coren         VARCHAR(30)  NULL,
                ativo         TINYINT(1)   NOT NULL DEFAULT 1,
                created_at    TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT uk_enfermeiro_coren UNIQUE (coren)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        self.con.commit()
        cur.close()

    # -------------------------------
    # INSERIR
    # -------------------------------
    def inserir(self, enf: Enfermeiro) -> int:
        sql = "INSERT INTO enfermeiro (nome, coren, ativo) VALUES (%s, %s, %s)"
        cur = self.con.cursor()
        try:
            cur.execute(sql, (enf.nome, enf.coren, enf.ativo))
            self.con.commit()
            return cur.lastrowid
        except Exception as e:
            self.con.rollback()
            raise RuntimeError(f"Erro ao inserir enfermeiro: {e}") from e
        finally:
            cur.close()

    # -------------------------------
    # BUSCAS
    # -------------------------------
    def buscar_por_nome(self, nome: str):
        sql = "SELECT * FROM enfermeiro WHERE nome = %s LIMIT 1"
        cur = self.con.cursor(dictionary=True)
        cur.execute(sql, (nome,))
        row = cur.fetchone()
        cur.close()
        return row

    def buscar_por_id(self, id_enfermeiro: int):
        sql = "SELECT * FROM enfermeiro WHERE id_enfermeiro = %s"
        cur = self.con.cursor(dictionary=True)
        cur.execute(sql, (id_enfermeiro,))
        row = cur.fetchone()
        cur.close()
        return row

    def listar(self, apenas_ativos: bool = False):
        if apenas_ativos:
            sql = "SELECT * FROM enfermeiro WHERE ativo = 1 ORDER BY nome"
        else:
            sql = "SELECT * FROM enfermeiro ORDER BY nome"
        cur = self.con.cursor(dictionary=True)
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        return rows

    # -------------------------------
    # ATUALIZAÇÕES
    # -------------------------------
    def atualizar_ativo(self, id_enfermeiro: int, ativo: int) -> bool:
        sql = "UPDATE enfermeiro SET ativo = %s WHERE id_enfermeiro = %s"
        cur = self.con.cursor()
        try:
            cur.execute(sql, (1 if ativo else 0, id_enfermeiro))
            self.con.commit()
            return cur.rowcount > 0
        except Exception as e:
            self.con.rollback()
            raise RuntimeError(f"Erro ao atualizar ativo: {e}") from e
        finally:
            cur.close()

    # -------------------------------
    # EXCLUIR
    # -------------------------------
    def excluir(self, id_enfermeiro: int) -> bool:
        sql = "DELETE FROM enfermeiro WHERE id_enfermeiro = %s"
        cur = self.con.cursor()
        try:
            cur.execute(sql, (id_enfermeiro,))
            self.con.commit()
            return cur.rowcount > 0
        except Exception as e:
            self.con.rollback()
            raise RuntimeError(f"Erro ao excluir enfermeiro: {e}") from e
        finally:
            cur.close()

    # -------------------------------
    # UTILITÁRIO: obter ou criar
    # usado pela TRIAGEM
    # -------------------------------
    def obter_ou_criar_por_nome(self, nome: str) -> int:
        nome = (nome or "").strip()
        if not nome:
            raise ValueError("Nome do enfermeiro é obrigatório.")

        existente = self.buscar_por_nome(nome)
        if existente:
            return existente["id_enfermeiro"]

        enf = Enfermeiro(nome=nome, coren=None, ativo=1)
        return self.inserir(enf)
