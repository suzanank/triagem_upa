# triagem_upa/model/paciente_model.py

class Paciente:
    def __init__(self, id_paciente=None, nome=None, cpf=None, data_nascimento=None, telefone=None):
        self.id_paciente = id_paciente
        self.nome = nome
        self.cpf = cpf
        self.data_nascimento = data_nascimento  # 'YYYY-MM-DD' ou None
        self.telefone = telefone

    def __str__(self):
        return f"[Paciente {self.id_paciente}] {self.nome} (CPF={self.cpf or '—'})"


class PacienteRepository:
    def __init__(self, conexao):
        self.con = conexao
        self._criar_tabela()

    def _criar_tabela(self):
        cur = self.con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS paciente (
                id_paciente     INT AUTO_INCREMENT PRIMARY KEY,
                nome            VARCHAR(120) NOT NULL,
                cpf             VARCHAR(14)  NULL,
                data_nascimento DATE         NULL,
                telefone        VARCHAR(20)  NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        self.con.commit()
        cur.close()

    # ---------- inserir ----------
    def inserir(self, pac: Paciente) -> int:
        sql = "INSERT INTO paciente (nome, cpf, data_nascimento, telefone) VALUES (%s, %s, %s, %s)"
        cur = self.con.cursor()
        try:
            cur.execute(sql, (pac.nome, pac.cpf, pac.data_nascimento, pac.telefone))
            self.con.commit()
            return cur.lastrowid
        except Exception as e:
            self.con.rollback()
            raise RuntimeError(f"Erro ao inserir paciente: {e}") from e
        finally:
            cur.close()

    # ---------- buscas ----------
    def buscar_por_id(self, id_paciente: int):
        cur = self.con.cursor(dictionary=True)
        cur.execute("SELECT * FROM paciente WHERE id_paciente=%s", (id_paciente,))
        row = cur.fetchone()
        cur.close()
        return row

    def buscar_por_nome(self, nome: str):
        cur = self.con.cursor(dictionary=True)
        cur.execute("SELECT * FROM paciente WHERE nome=%s LIMIT 1", (nome,))
        row = cur.fetchone()
        cur.close()
        return row

    def listar(self):
        cur = self.con.cursor(dictionary=True)
        cur.execute("SELECT * FROM paciente ORDER BY nome")
        rows = cur.fetchall()
        cur.close()
        return rows

    # ---------- atualizações ----------
    def atualizar_dados(self, id_paciente: int, nome: str, cpf: str | None, data_nascimento: str | None, telefone: str | None) -> bool:
        sql = "UPDATE paciente SET nome=%s, cpf=%s, data_nascimento=%s, telefone=%s WHERE id_paciente=%s"
        cur = self.con.cursor()
        try:
            cur.execute(sql, (nome, cpf, data_nascimento, telefone, id_paciente))
            self.con.commit()
            return cur.rowcount > 0
        except Exception as e:
            self.con.rollback()
            raise RuntimeError(f"Erro ao atualizar paciente: {e}") from e
        finally:
            cur.close()

    # ---------- excluir ----------
    def excluir(self, id_paciente: int) -> bool:
        cur = self.con.cursor()
        try:
            cur.execute("DELETE FROM paciente WHERE id_paciente=%s", (id_paciente,))
            self.con.commit()
            return cur.rowcount > 0
        except Exception as e:
            self.con.rollback()
            raise RuntimeError(f"Erro ao excluir paciente: {e}") from e
        finally:
            cur.close()

    # ---------- utilitário ----------
    def obter_ou_criar_por_nome(self, nome: str) -> int:
        nome = (nome or "").strip()
        if not nome:
            raise ValueError("Nome do paciente é obrigatório.")
        achado = self.buscar_por_nome(nome)
        if achado:
            return achado["id_paciente"]
        return self.inserir(Paciente(nome=nome))
