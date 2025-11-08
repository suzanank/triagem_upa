# triagem_upa/model/consulta_model.py

class Consulta:
    def __init__(
        self,
        id_consulta=None,
        id_atendimento=None,
        id_medico=None,
        pressao=None,
        peso=None,                 # DECIMAL(6,2)
        classificacao=None,        # 'VERDE' | 'AMARELO' | 'VERMELHO'
        sintomas=None,
        conduta=None,
        data_consulta=None
    ):
        self.id_consulta = id_consulta
        self.id_atendimento = id_atendimento
        self.id_medico = id_medico
        self.pressao = pressao
        self.peso = peso
        self.classificacao = classificacao
        self.sintomas = sintomas
        self.conduta = conduta
        self.data_consulta = data_consulta


class ConsultaRepository:
    def __init__(self, conexao):
        self.con = conexao
        self._criar_tabela()

    def _criar_tabela(self):
        cur = self.con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS consulta (
              id_consulta    INT AUTO_INCREMENT PRIMARY KEY,
              id_atendimento INT NOT NULL,
              id_medico      INT NOT NULL,
              pressao        VARCHAR(15) NULL,
              peso           DECIMAL(6,2) NULL,
              classificacao  ENUM('VERDE','AMARELO','VERMELHO') NULL,
              sintomas       TEXT NULL,
              conduta        TEXT NOT NULL,
              data_consulta  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
              INDEX idx_consulta_atend (id_atendimento),
              INDEX idx_consulta_medico (id_medico),
              CONSTRAINT fk_consulta_atendimento
                FOREIGN KEY (id_atendimento) REFERENCES atendimento(id_atendimento)
                ON UPDATE CASCADE ON DELETE RESTRICT,
              CONSTRAINT fk_consulta_medico
                FOREIGN KEY (id_medico) REFERENCES medico(id_medico)
                ON UPDATE CASCADE ON DELETE RESTRICT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        self.con.commit()
        cur.close()

    # ---------------- INSERT ----------------
    def inserir(self, c: Consulta) -> int:
        sql = """
            INSERT INTO consulta
              (id_atendimento, id_medico, pressao, peso, classificacao, sintomas, conduta)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cur = self.con.cursor()
        try:
            cur.execute(sql, (
                c.id_atendimento,
                c.id_medico,
                c.pressao,
                c.peso,
                c.classificacao,
                c.sintomas,
                c.conduta
            ))
            self.con.commit()
            return cur.lastrowid
        except Exception as e:
            self.con.rollback()
            raise RuntimeError(f"Erro ao inserir consulta: {e}") from e
        finally:
            cur.close()

    # ---------------- SELECTS ----------------
    def buscar_por_id(self, id_consulta: int):
        cur = self.con.cursor(dictionary=True)
        cur.execute("SELECT * FROM consulta WHERE id_consulta=%s", (id_consulta,))
        row = cur.fetchone()
        cur.close()
        return row

    def listar(self):
        cur = self.con.cursor(dictionary=True)
        cur.execute("""
            SELECT c.*, p.nome AS paciente, m.nome AS medico
            FROM consulta c
            JOIN atendimento a ON a.id_atendimento = c.id_atendimento
            JOIN paciente   p ON p.id_paciente    = a.id_paciente
            JOIN medico     m ON m.id_medico      = c.id_medico
            ORDER BY c.data_consulta DESC
        """)
        rows = cur.fetchall()
        cur.close()
        return rows

    def listar_por_atendimento(self, id_atendimento: int):
        cur = self.con.cursor(dictionary=True)
        cur.execute("SELECT * FROM consulta WHERE id_atendimento=%s ORDER BY data_consulta DESC", (id_atendimento,))
        rows = cur.fetchall()
        cur.close()
        return rows

    # ------- utilitário: pegar última triagem desse atendimento -------
    def obter_ultima_triagem(self, id_atendimento: int):
        cur = self.con.cursor(dictionary=True)
        cur.execute("""
            SELECT pressao, peso, classificacao, sintomas
            FROM triagem
            WHERE id_atendimento = %s
            ORDER BY data_triagem DESC
            LIMIT 1
        """, (id_atendimento,))
        row = cur.fetchone()
        cur.close()
        return row

    # ------- mudar status do atendimento -------
    def atualizar_status_atendimento(self, id_atendimento: int, novo_status: str) -> bool:
        cur = self.con.cursor()
        try:
            cur.execute("UPDATE atendimento SET status=%s WHERE id_atendimento=%s", (novo_status, id_atendimento))
            self.con.commit()
            return cur.rowcount > 0
        except Exception as e:
            self.con.rollback()
            raise RuntimeError(f"Erro ao atualizar status do atendimento: {e}") from e
        finally:
            cur.close()
