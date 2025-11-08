# triagem_upa/model/triagem_model.py

class Triagem:
    def __init__(
        self,
        id_triagem=None,
        id_atendimento=None,
        id_enfermeiro=None,
        pressao=None,
        temperatura=None,   # DECIMAL(3,1)
        peso=None,          # DECIMAL(6,2)
        sintomas=None,
        classificacao=None, # 'VERDE' | 'AMARELO' | 'VERMELHO'
        data_triagem=None
    ):
        self.id_triagem = id_triagem
        self.id_atendimento = id_atendimento
        self.id_enfermeiro = id_enfermeiro
        self.pressao = pressao
        self.temperatura = temperatura
        self.peso = peso
        self.sintomas = sintomas
        self.classificacao = classificacao
        self.data_triagem = data_triagem


class TriagemRepository:
    def __init__(self, conexao):
        self.con = conexao
        self._criar_tabela()

    def _criar_tabela(self):
        cur = self.con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS triagem (
              id_triagem    INT AUTO_INCREMENT PRIMARY KEY,
              id_atendimento INT NOT NULL,
              id_enfermeiro  INT NOT NULL,
              classificacao  ENUM('VERDE','AMARELO','VERMELHO') NOT NULL,
              pressao        VARCHAR(15) NULL,
              temperatura    DECIMAL(3,1) NULL,
              peso           DECIMAL(6,2) NULL,
              sintomas       TEXT NULL,
              data_triagem   DATETIME DEFAULT CURRENT_TIMESTAMP,
              INDEX idx_trg_atend (id_atendimento),
              CONSTRAINT fk_trg_atend FOREIGN KEY (id_atendimento) REFERENCES atendimento(id_atendimento),
              CONSTRAINT fk_trg_enf   FOREIGN KEY (id_enfermeiro)  REFERENCES enfermeiro(id_enfermeiro)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        self.con.commit()
        cur.close()

    # ----------------- INSERT -----------------
    def inserir(self, t: Triagem) -> int:
        sql = """
            INSERT INTO triagem
              (id_atendimento, id_enfermeiro, classificacao, pressao, temperatura, peso, sintomas)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cur = self.con.cursor()
        try:
            cur.execute(sql, (
                t.id_atendimento,
                t.id_enfermeiro,
                t.classificacao,
                t.pressao,
                t.temperatura,
                t.peso,
                t.sintomas
            ))
            self.con.commit()
            return cur.lastrowid
        except Exception as e:
            self.con.rollback()
            raise RuntimeError(f"Erro ao inserir triagem: {e}") from e
        finally:
            cur.close()

    # -------- utilitários usados pelo controller --------
    def atualizar_data_nascimento(self, id_paciente: int, data_nascimento: str):
        cur = self.con.cursor()
        try:
            cur.execute("UPDATE paciente SET data_nascimento=%s WHERE id_paciente=%s", (data_nascimento, id_paciente))
            self.con.commit()
        except Exception as e:
            self.con.rollback()
            raise RuntimeError(f"Erro ao atualizar data de nascimento: {e}") from e
        finally:
            cur.close()

    def carregar_header_por_senha(self, senha: str):
        """
        Retorna cabeçalho da triagem a partir da senha do atendimento:
        nome do paciente, prioridade, senha e status atual do atendimento.
        """
        sql = """
            SELECT p.nome, a.prioridade, a.senha, a.status, a.id_atendimento, a.id_paciente
            FROM atendimento a
            JOIN paciente p ON p.id_paciente = a.id_paciente
            WHERE a.senha = %s
            LIMIT 1
        """
        cur = self.con.cursor(dictionary=True)
        cur.execute(sql, (senha,))
        row = cur.fetchone()
        cur.close()
        return row
