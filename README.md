# SpiderPay - API de Pagamentos Simulada

## Descrição

SpiderPay é um projeto de API de pagamentos RESTful desenvolvido como parte de um portfólio para demonstrar habilidades de desenvolvimento backend de nível Pleno. A API simula o fluxo de criação e consulta de pagamentos, interagindo com um sistema de gateway de pagamento abstraído e mockado internamente.

O objetivo principal é apresentar uma arquitetura de software robusta, modular, testável e extensível, utilizando tecnologias modernas e boas práticas de engenharia de software. A arquitetura permite a fácil substituição ou adição de novos gateways de pagamento no futuro.

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

## Funcionalidades Planejadas

*   [ ] Estrutura básica do projeto FastAPI.
*   [ ] Configuração de banco de dados PostgreSQL com SQLAlchemy async (`app/core/database.py`).
*   [ ] Configuração de variáveis de ambiente com Pydantic Settings (`app/core/config.py`).
*   [ ] Configuração inicial de migrations com Alembic (`alembic.ini`, `migrations/env.py`).
*   [ ] Módulo `Users`:
    *   Model (`users/models.py`)
    *   Schema (`users/schema.py`)
    *   Repository (`users/repository.py`)
    *   Service (`users/service.py`)
    *   Router (`users/router.py`) com CRUD básico.
*   [ ] Módulo `Payments`:
    *   Model, Schema, Repository, Service, Router.
    *   `POST /payments`: Criação de um novo pagamento (status inicial PENDING).
    *   `GET /payments/{payment_id}`: Consulta de um pagamento específico.
    *   `GET /payments`: Listagem de pagamentos (com paginação).
*   [ ] Módulo `Transactions`:
    *   Model, Schema, Repository, Service.
    *   Criação automática de transações durante o fluxo de pagamento.
*   [ ] Módulo `Gateway`:
    *   Interface `AbstractGateway` (`gateway/base.py`).
    *   Implementação `MockGateway` (`gateway/mock.py`) simulando sucesso/falha, latência e possivelmente webhooks internos.
    *   Factory `get_gateway` (`gateway/factory.py`) para seleção dinâmica baseada em `.env`.
*   [ ] Integração do `PaymentService` com o `GatewayService` (via abstração) para iniciar pagamentos.
*   [ ] Atualização do status do Pagamento e criação de Transações com base na resposta (simulada) do Gateway.
*   [ ] Simulação de Webhooks (Opcional): O `MockGateway` pode chamar diretamente um serviço (`WebhookService`?) para simular notificações assíncronas de confirmação/falha.
*   [ ] Módulo `Webhooks` (Opcional): Endpoint e serviço para processar notificações (inicialmente invocado pelo mock).
*   [ ] Autenticação básica de API (ex: Bearer token JWT - futuro, em `core/security.py` e middlewares).
*   [ ] Testes unitários e de integração (Pytest).
*   [ ] Documentação da API (automática via FastAPI/Swagger e OpenAPI).
*   [ ] Tratamento de erros e logging consistentes.

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

5.  **Configure o Alembic:**
    *   Se for a primeira vez, inicialize o Alembic:
        ```bash
        alembic init migrations
        ```
    *   Edite o arquivo `alembic.ini` gerado:
        *   Ajuste `sqlalchemy.url` para ler a variável de ambiente: `sqlalchemy.url = postgresql+asyncpg://user:password@host:port/database_name` (ou configure `env.py` para ler do `settings`).
    *   Edite o arquivo `migrations/env.py`:
        *   Importe `Base` de `app.core.database` e os modelos (`YourModel`) de `app.modules.*.models`.
        *   Configure `target_metadata = Base.metadata` dentro da função `run_migrations_online`.
        *   Configure `target_metadata = Base.metadata` também na seção `run_migrations_offline` (opcional, mas bom ter).
        *   Garanta que `env.py` consiga importar seus módulos (pode precisar ajustar `sys.path`).

6.  **Execute as migrations iniciais:**
    *   Gere a primeira revisão automática (depois de definir seus modelos SQLAlchemy):
        ```bash
        alembic revision --autogenerate -m "Initial database schema"
        ```
    *   Aplique a revisão ao banco de dados:
        ```bash
        alembic upgrade head
        ```

7.  **Execute a aplicação:**
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```

8.  **Acesse a documentação interativa da API (Swagger UI):**
    Abra o navegador em `http://localhost:8000/docs`

9.  **Acesse a documentação alternativa da API (ReDoc):**
    Abra o navegador em `http://localhost:8000/redoc`

```
spiderpay/
├── app/
│ ├── init.py
│ ├── main.py # Ponto de entrada FastAPI, montagem dos routers
│ ├── core/ # Lógica central compartilhada
│ │ ├── init.py
│ │ ├── config.py # Gestão de configurações (env vars)
│ │ ├── database.py # Configuração da sessão do BD (SQLAlchemy async)
│ │ └── security.py # Utilitários de segurança (JWT, hashing - futuro)
│ ├── modules/ # Módulos funcionais da aplicação
│ │ ├── init.py
│ │ ├── payments/ # Módulo de Pagamentos
│ │ │ ├── init.py
│ │ │ ├── router.py # Endpoints da API (/payments)
│ │ │ ├── service.py # Lógica de negócio
│ │ │ ├── schema.py # Schemas Pydantic (DTOs)
│ │ │ ├── models.py # Modelos SQLAlchemy
│ │ │ └── repository.py # Camada de acesso a dados
│ │ ├── transactions/ # Módulo de Transações (estrutura similar)
│ │ │ └── ...
│ │ ├── users/ # Módulo de Usuários (estrutura similar)
│ │ │ └── ...
│ │ ├── gateway/ # Abstração e implementações de Gateways
│ │ │ ├── init.py
│ │ │ ├── base.py # Interface Abstrata (AbstractGateway)
│ │ │ ├── mock.py # Implementação MockGateway (simulação interna)
│ │ │ └── factory.py # Factory para obter a instância do gateway ativo
│ │ └── webhooks/ # Módulo para receber notificações externas (opcional/futuro)
│ │ ├── init.py
│ │ ├── router.py # Endpoints de webhook (/webhooks/gateway)
│ │ └── service.py # Lógica de processamento de webhooks
│ └── schemas/ # Schemas Pydantic globais (opcional)
│ └── init.py
├── tests/ # Testes unitários e de integração
│ ├── init.py
│ └── conftest.py
├── migrations/ # Scripts de migration Alembic (gerenciados pelo Alembic)
│ └── versions/
│ └── script.py.mako
│ └── env.py
├── .env # Variáveis de ambiente locais (NÃO versionar)
├── .env.example # Exemplo de variáveis de ambiente
├── .gitignore
├── requirements.txt # Dependências Python
├── alembic.ini # Configuração do Alembic
└── README.md # Este arquivo
```
