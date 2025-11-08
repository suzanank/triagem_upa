🏥 Sistema de Triagem UPA

Sistema desenvolvido em Python (Tkinter + MySQL) para gerenciar o fluxo básico de atendimento em uma Unidade de Pronto Atendimento (UPA), incluindo:

✅ Cadastro de Pacientes
✅ Atendimento (geração de senha por prioridade)
✅ Triagem (enfermeiro)
✅ Consulta médica
✅ Controle de Médicos e Enfermeiros
✅ Fluxo automatizado entre etapas

📌 Funcionalidades do Sistema
✅ 1. Atendimento

Seleção do paciente

Escolha da prioridade: NORMAL ou PRIORITÁRIO

Geração automática da senha:

P-XXX para prioritário

N-XXX para normal

Status inicial: AGUARDANDO

✅ 2. Triagem

Carrega automaticamente:

Paciente

Senha do atendimento

Prioridade

Enfermeiro é selecionado automaticamente baseado no status ativo

Enfermeiro registra:

Pressão arterial

Temperatura

Peso

Sintomas

Classificação: VERDE, AMARELO ou VERMELHO

Atualiza o atendimento para status TRIAGEM

✅ 3. Consulta

Lista todos atendimentos já triados

Carrega:

Paciente

Prioridade

Senha

Dados da triagem

Médico selecionado conforme disponibilidade

Realiza diagnóstico e conduta

✅ 4. Cadastro de Profissionais

Médico (NOME, CRM, especialidade, ativo)

Enfermeiro (NOME, COREN, ativo)

🗃️ Estrutura do Banco de Dados (MySQL)

O banco contém as tabelas:

paciente

medico

enfermeiro

atendimento

triagem

consulta

Todas com integridade referencial e relacionamento entre as etapas do fluxo.

🧩 Arquitetura do Projeto
triagem_upa/
│
├── controller/
│   ├── atendimento_controller.py
│   ├── triagem_controller.py
│   ├── consulta_controller.py
│   ├── paciente_controller.py
│   ├── medico_controller.py
│   ├── enfermeiro_controller.py
│
├── model/
│   ├── dbconection.py
│   ├── atendimento_model.py
│   ├── triagem_model.py
│   ├── consulta_model.py
│   ├── paciente_model.py
│   ├── medico_model.py
│   ├── enfermeiro_model.py
│
└── view/
    ├── atendimento_view.py
    ├── triagem_view.py
    ├── consulta_view.py
    ├── paciente_view.py
    ├── medico_view.py
    ├── enfermeiro_view.py


Padrão usado: MVC (Model–View–Controller)

🚀 Como Rodar o Sistema
✅ 1. Instale o Python 3.13+

https://www.python.org/downloads/

✅ 2. Instale o MySQL

https://dev.mysql.com/downloads/

✅ 3. Instale dependências
pip install mysql-connector-python

✅ 4. Configure o banco no arquivo:

model/dbconection.py

Exemplo:

conexao = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456",
    database="triagem_upa"
)

✅ 5. Crie o banco pelo script SQL do repositório
SOURCE triagem_upa.sql;

✅ 6. Execute qualquer view (exemplo):
python view/atendimento_view.py

🎯 Objetivo do Projeto

Este sistema foi desenvolvido para fins:

✅ didáticos
✅ acadêmicos
✅ demonstrar aplicação real de MVC + Python + MySQL
✅ praticar CRUD, Tkinter e integração com banco


