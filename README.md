# SpiderPay - API de Pagamentos Simulada

## Descrição

SpiderPay é uma API RESTful para simulação de pagamentos, desenvolvida com foco em boas práticas de engenharia de software, arquitetura modular e extensibilidade. O projeto abstrai um gateway de pagamento fictício, permitindo a simulação completa de criação e consulta de transações, com suporte futuro para integrações reais.

## Tecnologias Utilizadas

*   **Linguagem:** Python 3.10+
*   **Framework API:** FastAPI
*   **Banco de Dados:** PostgreSQL
*   **ORM:** SQLAlchemy (com `asyncio` e `AsyncSession`)
*   **Migrations:** Alembic
*   **Validação de Dados:** Pydantic v2+
*   **Configuração:** Pydantic Settings (leitura de `.env`)
*   **Testes:** Pytest (planejado)
*   **Servidor ASGI:** Uvicorn

## Arquitetura

O projeto segue uma arquitetura modular e em camadas, visando a separação de responsabilidades (SoC) e alta coesão dentro dos módulos.

**Componentes Principais:**

*   **Router:** Define os endpoints HTTP, valida dados de entrada/saída com schemas Pydantic e delega para a camada de Serviço. Utiliza `APIRouter` do FastAPI.
*   **Service:** Orquestra a lógica de negócio, interagindo com Repositórios e outros Serviços (incluindo o Gateway). É onde as regras de negócio são implementadas.
*   **Repository:** Encapsula toda a lógica de acesso ao banco de dados usando SQLAlchemy ORM (modo assíncrono). É a única camada que interage diretamente com os `models`.
*   **Gateway Abstraction:** Uma classe base abstrata (`AbstractGateway` em `gateway/base.py`) define o contrato para interações com gateways de pagamento (ex: `initiate_payment`, `get_payment_status`). Implementações concretas (como `MockGateway` em `gateway/mock.py`) herdam dessa interface. Uma factory (`get_gateway` em `gateway/factory.py`) seleciona a implementação ativa com base na configuração (`.env`), permitindo adicionar gateways reais (Stripe, PayPal, etc.) no futuro com modificações mínimas no resto do sistema.
*   **Models:** Definições das tabelas do banco de dados (Usuários, Pagamentos, Transações) usando SQLAlchemy (com `declarative_base`).
*   **Schemas:** Definições Pydantic (`BaseModel`) usadas para validação de dados de API (corpo de requests, query params) e serialização de respostas (Data Transfer Objects - DTOs), garantindo contratos de dados claros.


## Setup e Execução

1.  **Clone o repositório:**
    ```bash
    git clone <url-do-repositorio>
    cd spiderpay
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate # Linux/macOS
    # venv\Scripts\activate # Windows
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as variáveis de ambiente:**
    *   Copie `.env.example` para `.env`.
    *   Edite o arquivo `.env` com as configurações do seu banco de dados PostgreSQL (`DATABASE_URL`) e defina o gateway ativo (`ACTIVE_GATEWAY=mock`).
    *   Exemplo de `DATABASE_URL`: `postgresql+asyncpg://user:password@host:port/database_name`
    *   Certifique-se de que o usuário e o banco de dados existem no PostgreSQL.

5.  **Execute as migrations:**
    ```bash
    alembic upgrade head
    ```

6.  **Execute a aplicação:**
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```

7.  **Acesse a documentação interativa da API (Swagger UI):**
    Abra o navegador em `http://localhost:8000/docs`

8.  **Acesse a documentação alternativa da API (ReDoc):**
    Abra o navegador em `http://localhost:8000/redoc`

```
spiderpay/
├── app/
│   ├── main.py                 # Ponto de entrada FastAPI
│   ├── core/                   # Configuração central
│   │   ├── config.py           # Variáveis de ambiente (.env)
│   │   ├── database.py         # Sessão assíncrona com PostgreSQL
│   │   └── security.py         # (Futuro: JWT, hash de senhas)
│   ├── modules/
│   │   ├── payments/           # CRUD de pagamentos
│   │   ├── transactions/       # Controle de transações
│   │   ├── users/              # Cadastro e autenticação de usuários
│   │   ├── gateway/            # Abstração de gateways de pagamento
│   │   │   ├── base.py         # Interface abstrata
│   │   │   ├── mock.py         # Implementação mock
│   │   │   └── factory.py      # Instancia o gateway com base no .env
│   │   └── webhooks/           # (Opcional: integração com notificações externas)
│   └── schemas/                # Schemas globais (DTOs Pydantic)
├── migrations/                 # Scripts gerados pelo Alembic
├── tests/                      # (Futuro) Testes automatizados
├── .env                        # Configurações locais (NÃO versionar)
├── .env.example                # Exemplo de variáveis
├── requirements.txt            # Dependências
├── alembic.ini                 # Configuração do Alembic
└── README.md                   # Este arquivo

```
