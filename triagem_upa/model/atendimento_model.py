from datetime import datetime
import mysql.connector


class Atendimento:
    """
    Representa um atendimento básico gerado no totem ou balcão.
    """
    def __init__(
        self,
        id_atendimento: int = None,
        id_paciente: int = None,
        senha: str = None,
        prioridade: str = None,
        data_chegada=None,
        status: str = "AGUARDANDO"
    ):
        self.id_atendimento = id_atendimento
        self.id_paciente = id_paciente
        self.senha = senha
        self.prioridade = prioridade
        self.data_chegada = data_chegada
        self.status = status

    def __str__(self):
        return (
            f"[Atendimento {self.id_atendimento}] Paciente={self.id_paciente} | "
            f"Senha={self.senha} | Prioridade={self.prioridade} | "
            f"Status={self.status} | Chegada={self.data_chegada}"
        )


class AtendimentoRepository:
    """
    Acesso ao banco para operações CRUD simples e consultas
    relacionadas ao atendimento.
    """

    def __init__(self, conexao):
        self.con = conexao
        self._criar_tabela()

    # ---------------------------------------------------------
    # CRIAÇÃO DA TABELA (garantia)
    # ---------------------------------------------------------
    def _criar_tabela(self):
        cur = self.con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS atendimento (
                id_atendimento INT NOT NULL AUTO_INCREMENT,
                id_paciente    INT NOT NULL,
                senha          VARCHAR(10) NOT NULL,
                prioridade     ENUM('NORMAL','PRIORITARIO') NOT NULL,
                data_chegada   DATETIME DEFAULT CURRENT_TIMESTAMP,
                status         ENUM('AGUARDANDO','TRIAGEM','MEDICO','FINALIZADO') 
                               DEFAULT 'AGUARDANDO',

                PRIMARY KEY (id_atendimento),
                FOREIGN KEY (id_paciente) REFERENCES paciente(id_paciente)
                    ON UPDATE CASCADE ON DELETE RESTRICT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        self.con.commit()
        cur.close()

    # ---------------------------------------------------------
    # INSERIR NOVO ATENDIMENTO
    # ---------------------------------------------------------
    def inserir(self, atendimento: Atendimento) -> int:
        sql = """
            INSERT INTO atendimento (id_paciente, senha, prioridade, data_chegada, status)
            VALUES (%s, %s, %s, %s, %s)
        """

        dados = (
            atendimento.id_paciente,
            atendimento.senha,
            atendimento.prioridade,
            atendimento.data_chegada or datetime.now(),
            atendimento.status,
        )

        cur = self.con.cursor()
        try:
            cur.execute(sql, dados)
            self.con.commit()
            return cur.lastrowid
        except Exception as e:
            self.con.rollback()
            raise RuntimeError(f"Erro ao inserir atendimento: {e}") from e
        finally:
            cur.close()

    # ---------------------------------------------------------
    # LISTAR TODOS
    # ---------------------------------------------------------
    def listar_todos(self):
        sql = """
            SELECT id_atendimento, id_paciente, senha, prioridade,
                   data_chegada, status
            FROM atendimento
            ORDER BY data_chegada DESC
        """
        cur = self.con.cursor(dictionary=True)
        cur.execute(sql)
        resultado = cur.fetchall()
        cur.close()
        return resultado

    # ---------------------------------------------------------
    # BUSCAR POR SENHA
    # ---------------------------------------------------------
    def buscar_por_senha(self, senha: str):
        sql = """
            SELECT *
            FROM atendimento
            WHERE senha = %s
            LIMIT 1
        """
        cur = self.con.cursor(dictionary=True)
        cur.execute(sql, (senha,))
        row = cur.fetchone()
        cur.close()
        return row

    # ---------------------------------------------------------
    # BUSCAR POR ID
    # ---------------------------------------------------------
    def buscar_por_id(self, id_atendimento: int):
        sql = """
            SELECT *
            FROM atendimento
            WHERE id_atendimento = %s
        """
        cur = self.con.cursor(dictionary=True)
        cur.execute(sql, (id_atendimento,))
        row = cur.fetchone()
        cur.close()
        return row

    # ---------------------------------------------------------
    # ATUALIZAR STATUS
    # ---------------------------------------------------------
    def atualizar_status(self, id_atendimento: int, novo_status: str) -> bool:
        sql = """
            UPDATE atendimento
            SET status = %s
            WHERE id_atendimento = %s
        """
        cur = self.con.cursor()
        try:
            cur.execute(sql, (novo_status, id_atendimento))
            self.con.commit()
            return cur.rowcount > 0
        except Exception as e:
            self.con.rollback()
            raise RuntimeError(f"Erro ao atualizar status do atendimento: {e}") from e
        finally:
            cur.close()

    # ---------------------------------------------------------
    # EXCLUIR
    # ---------------------------------------------------------
    def excluir(self, id_atendimento: int) -> bool:
        sql = "DELETE FROM atendimento WHERE id_atendimento = %s"
        cur = self.con.cursor()
        try:
            cur.execute(sql, (id_atendimento,))
            self.con.commit()
            return cur.rowcount > 0
        except Exception as e:
            self.con.rollback()
            raise RuntimeError(f"Erro ao excluir atendimento: {e}") from e
        finally:
            cur.close()

    # ---------------------------------------------------------
    # GERAR SENHA DO DIA
    # ---------------------------------------------------------
    def gerar_proxima_senha(self, prioridade: str) -> str:
        """
        Gera senha sequencial por dia:
        Normal  →  N001, N002...
        Prioritário →  P001, P002...
        """

        prefixo = "N" if prioridade == "NORMAL" else "P"

        sql = """
            SELECT senha
            FROM atendimento
            WHERE DATE(data_chegada) = CURDATE()
              AND senha LIKE %s
            ORDER BY id_atendimento DESC
            LIMIT 1
        """

        cur = self.con.cursor()
        cur.execute(sql, (f"{prefixo}%",))
        ultima = cur.fetchone()

        if not ultima:
            return f"{prefixo}001"

        # extrai número
        ultima_senha = ultima[0]
        numero = int(ultima_senha[1:]) + 1
        return f"{prefixo}{numero:03d}"
