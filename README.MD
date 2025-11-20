# 🚀 Fake Store API - Integração Resiliente com FastAPI

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.120.3-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Latest-blue.svg)
![Redis](https://img.shields.io/badge/Redis-Latest-red.svg)
![Celery](https://img.shields.io/badge/Celery-5.5.3-green.svg)

Uma API RESTful moderna, escalável e resiliente que integra dados da [FakeStoreAPI](https://fakestoreapi.com/), implementando estratégias avançadas de cache, processamento assíncrono e fallback automático para garantir alta disponibilidade mesmo em cenários de falha da API externa.

## Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Características Principais](#-características-principais)
- [Arquitetura](#-arquitetura)
- [Tecnologias](#-tecnologias)
- [Estratégia de Resiliência](#-estratégia-de-resiliência-e-cache)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Endpoints](#-endpoints)
- [Documentação](#-documentação)

## Sobre o Projeto

Este projeto demonstra a implementação de uma arquitetura robusta para integração com APIs externas, focando em:

- **Alta Disponibilidade**: Sistema continua funcionando mesmo quando a API externa está indisponível
- **Performance Otimizada**: Cache em memória (Redis) com atualização assíncrona via Celery
- **Escalabilidade Horizontal**: Arquitetura modular que permite escalar componentes independentemente
- **Segurança**: Autenticação JWT com controle de acesso baseado em perfis (ADMIN/USER)
- **Manutenibilidade**: Padrão Clean Architecture com separação clara de responsabilidades

## Características Principais

### Autenticação e Autorização

- **Autenticação JWT**: Sistema stateless com tokens de acesso e refresh
- **Controle de Acesso por Perfil**:
  - **ADMIN**: Visualiza e gerencia favoritos de todos os usuários
  - **USER**: Visualiza e gerencia apenas seus próprios favoritos

### Performance e Escalabilidade

- **Cache em Memória (Redis)**: Redução drástica de latência para consultas frequentes
- **Processamento Assíncrono (Celery)**: Atualização de cache e persistência em background
- **Arquitetura Modular**: Padrão Controller → Use Case → Service
- **Escalabilidade Independente**: Cada componente pode ser escalado separadamente:
  - Múltiplas réplicas do FastAPI para maior throughput
  - Workers Celery dedicados para tarefas pesadas
  - Clusters Redis e PostgreSQL para alta disponibilidade

### Resiliência

- **Fallback Automático**: Em caso de falha da API externa, retorna dados do banco local
- **TTL Configurável**: Tempo de vida do cache ajustável via variáveis de ambiente
- **Tratamento de Erros**: Respostas consistentes mesmo em cenários de erro

### Integridade dos Dados

- **PostgreSQL**: Banco relacional com integridade referencial
- **Índices Otimizados**: Consultas eficientes em campos de busca
- **Migrações Versionadas**: Alembic para controle de schema

## Arquitetura

O projeto segue os princípios de **Clean Architecture** e **SOLID**, organizando o código em camadas bem definidas:

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI (Controller)                 │
│              Camada de apresentação/HTTP                │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                    Use Case Layer                       │
│         Orquestração de regras de negócio               │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                    Service Layer                        │
│    Lógica de negócio e integração com serviços          │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼────────┐          ┌─────────▼─────────┐
│   PostgreSQL   │          │      Redis        │
│  (Persistência)│          │     (Cache)       │
└────────────────┘          └───────────────────┘
                                    │
                            ┌───────▼────────┐
                            │     Celery     │
                            │  (Background)  │
                            └────────────────┘
```

### Fluxo de Dados

1. **Requisição HTTP** → Controller recebe e valida
2. **Use Case** → Orquestra a lógica de negócio
3. **Service** → Executa operações específicas
4. **Cache/DB** → Acessa dados conforme estratégia de resiliência

## Tecnologias


| Categoria                | Tecnologia      | Versão | Uso                          |
| -------------------------- | ----------------- | --------- | ------------------------------ |
| **Linguagem**            | Python          | 3.11+   | Linguagem principal          |
| **Framework Web**        | FastAPI         | 0.120.3 | API REST assíncrona         |
| **Banco de Dados**       | PostgreSQL      | Latest  | Persistência principal      |
| **Cache/Fila**           | Redis           | Latest  | Cache e broker do Celery     |
| **Tarefas Assíncronas** | Celery          | 5.5.3   | Processamento em background  |
| **ORM**                  | SQLAlchemy      | 2.0.44  | Mapeamento objeto-relacional |
| **Migrações**          | Alembic         | 1.17.1  | Versionamento de schema      |
| **Autenticação**       | PyJWT           | 2.10.1  | Tokens JWT                   |
| **Validação**          | Pydantic        | 2.12.3  | Validação de dados         |
| **Documentação**       | Swagger/OpenAPI | -       | Documentação interativa    |

## Estratégia de Resiliência e Cache

A aplicação implementa uma estratégia de **Cache-Aside Pattern** com fallback automático:

### Fluxo de Consulta de Produtos

```
┌─────────────┐
│   Cliente   │
└──────┬──────┘
       │ 1. Requisição
       ▼
┌─────────────────┐
│   FastAPI App   │
└──────┬──────────┘
       │ 2. Verifica Cache
       ▼
┌─────────────────┐     Cache Hit? ──► Retorna dados do Redis
│      Redis      │
└─────────────────┘     Cache Miss?
       │ 3. Consulta API Externa
       ▼
┌─────────────────┐     Sucesso? ──► Atualiza Cache + DB (async)
│  FakeStoreAPI   │
└─────────────────┘     Falha?
       │ 4. Fallback
       ▼
┌─────────────────┐     Retorna dados do PostgreSQL
│   PostgreSQL    │
└─────────────────┘
```

### Detalhamento do Fluxo

#### 1 **Consulta ao Redis (Cache Hit)**

- Sistema verifica se os dados estão em cache
- TTL configurável via variável de ambiente
- **Resposta imediata** se dados válidos encontrados

#### 2 **Cache Miss - Requisição à API Externa**

- Se cache ausente ou expirado, consulta a FakeStoreAPI
- Ao obter resposta bem-sucedida:
  - Retorna dados ao cliente imediatamente
  - Envia tarefa assíncrona ao Celery para:
    - Atualizar cache Redis
    - Persistir/atualizar no PostgreSQL

#### 3 **Falha na API Externa - Fallback Automático**

- Se FakeStoreAPI estiver indisponível:
  - Sistema consulta PostgreSQL automaticamente
  - Retorna dados locais (última versão conhecida)
  - Cliente recebe resposta consistente sem erro

> **Nota**: Este comportamento é aplicado tanto em `/api/v1/fakestoreapi` (lista) quanto em `/api/v1/fakestoreapi/{id}` (detalhe).

## Pré-requisitos

### Opção 1: Instalação Local

- **Python** 3.11 ou superior
- **PostgreSQL** (instância local ou remota)
- **Redis** (instância local ou remota)
- **Git** (para clonar o repositório)

### Opção 2: Instalação com Docker (Recomendado)

- **Docker** 20.10 ou superior
- **Docker Compose** 2.0 ou superior
- **Git** (para clonar o repositório)

> 💡 **Recomendação**: Use Docker para uma instalação mais rápida e sem necessidade de configurar PostgreSQL e Redis manualmente.

## Instalação

### 1. Clone o repositório

```bash
git clone git@github.com:ivancley/fakestoreapi-fastapi.git
cd fakestoreapi-fastapi
```

### 2. Crie e ative o ambiente virtual

```bash
# Criar ambiente virtual
python3 -m venv .venv

# Ativar ambiente virtual
# Linux/Mac:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Crie um arquivo `.env` baseado no `.env_example` e configure:

```bash
# Exemplo de variáveis necessárias
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-secret-key-here
CACHE_TTL=3600  # TTL do cache em segundos
```

### 5. Execute as migrações

```bash
alembic upgrade head
```

### 6. Inicie os serviços

**Terminal 1 - Celery Worker:**

```bash
celery -A api.utils.celery worker --loglevel=info
```

**Terminal 2 - FastAPI Server:**

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Usuário Administrador

Ao executar as migrações, um usuário administrador é criado automaticamente com as seguintes credenciais:

- **Email**: `admin@gmail.com`
- **Senha**: `Senha@123`
- **Permissões**: `ADMIN`

> **Nota**: Este usuário é criado pela migração `create_admin_user`. Se o usuário já existir, a migração não criará duplicatas.

## Instalação com Docker

A forma mais simples de executar a aplicação é utilizando Docker Compose, que configura automaticamente todos os serviços necessários.

### Pré-requisitos

- **Docker** 20.10 ou superior
- **Docker Compose** 2.0 ou superior

### Passos para Execução

1. **Clone o repositório** (se ainda não fez):

```bash
git clone git@github.com:ivancley/fakestoreapi-fastapi.git
cd fakestoreapi-fastapi
```

2. **Configure as variáveis de ambiente** (opcional):

Crie um arquivo `.env` na raiz do projeto para personalizar configurações:

```bash
# .env
JWT_SECRET_KEY=sua-chave-secreta-aqui
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=20
REFRESH_TOKEN_EXPIRE_DAYS=1
REDIS_TTL=300
```

> **Nota**: Se não criar o arquivo `.env`, valores padrão serão utilizados. **Importante**: Altere `JWT_SECRET_KEY` em produção!

3. **Inicie todos os serviços**:

```bash
docker-compose up -d
```

Este comando irá:

- Construir a imagem da aplicação
- Iniciar PostgreSQL na porta 5432
- Iniciar Redis na porta 6379
- Iniciar a API FastAPI na porta 8000
- Iniciar o worker Celery
- Executar as migrações do banco automaticamente
- Criar usuário administrador automaticamente (via migração)

4. **Verifique o status dos containers**:

```bash
docker-compose ps
```

5. **Acompanhe os logs** (opcional):

```bash
# Logs de todos os serviços
docker-compose logs -f

# Logs apenas da API
docker-compose logs -f api

# Logs apenas do Celery
docker-compose logs -f celery
```

6. **Usuário Administrador**:

Ao executar as migrações (que acontecem automaticamente ao iniciar os containers), um usuário administrador é criado automaticamente com as seguintes credenciais:

- **Email**: `admin@gmail.com`
- **Senha**: `Senha@123`
- **Permissões**: `ADMIN`

> **Nota**: Este usuário é criado pela migração `2312760d89d5_create_admin_user.py`. Você pode fazer login imediatamente após os containers iniciarem usando essas credenciais.

### Comandos Úteis

```bash
# Parar todos os serviços
docker-compose down

# Parar e remover volumes (apaga dados do banco)
docker-compose down -v

# Reconstruir as imagens
docker-compose build --no-cache

# Reiniciar um serviço específico
docker-compose restart api

# Executar comandos dentro do container
docker-compose exec api bash
docker-compose exec api alembic upgrade head
```

### Acessar a Aplicação

Após iniciar os serviços, a API estará disponível em:

- **API**: http://localhost:8000
- **Documentação Swagger**: http://localhost:8000/docs
- **Documentação ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

###  Credenciais do Usuário Administrador

Um usuário administrador é criado automaticamente durante a execução das migrações do banco de dados. Use estas credenciais para fazer login:


| Campo           | Valor             |
| ----------------- | ------------------- |
| **Email**       | `admin@gmail.com` |
| **Senha**       | `Senha@123`       |
| **Permissões** | `ADMIN`           |

>  **Importante**: Altere a senha padrão em ambientes de produção! O usuário é criado pela migração `2312760d89d5_create_admin_user.py` e não será duplicado se já existir.

### Estrutura dos Serviços no Docker

```
┌─────────────────────────────────────────┐
│         Docker Compose Network          │
│                                         │
│  ┌──────────┐  ┌──────────┐             │
│  │   API    │  │  Celery  │             │
│  │ (FastAPI)│  │  Worker  │             │
│  └────┬─────┘  └────┬─────┘             │
│       │             │                   │
│       └─────┬───────┘                   │
│             │                           │
│  ┌──────────▼───────────┐               │
│  │      PostgreSQL      │               │
│  └──────────────────────┘               │
│                                         │
│  ┌──────────▼───────────┐               │
│  │        Redis         │               │
│  │  (Cache + Broker)    │               │
│  └──────────────────────┘               │
└─────────────────────────────────────────┘
```

## Estrutura do Projeto

```
fakestoreapi-fastapi-ia/
│
├── api/
│   ├── utils/              # Utilitários compartilhados
│   │   ├── celery.py      # Configuração do Celery
│   │   ├── db_services.py # Conexões com banco
│   │   ├── exceptions.py  # Tratamento de exceções
│   │   └── security.py    # Autenticação JWT
│   │
│   └── v1/                # Versão 1 da API
│       ├── _shared/       # Modelos e schemas compartilhados
│       ├── account/       # Autenticação e registro
│       ├── user/          # Gerenciamento de usuários
│       ├── fakestoreapi/  # Integração com FakeStoreAPI
│       │   └── services/  # Serviços de API, cache e background
│       └── favorite/      # Sistema de favoritos
│
├── migrations/            # Migrações do Alembic
├── main.py               # Aplicação FastAPI principal
├── create_inicial_user.py # Script de criação de usuário inicial (opcional, usuário admin é criado via migração)
├── requirements.txt      # Dependências do projeto
└── alembic.ini          # Configuração do Alembic
```

## Endpoints Principais

### Autenticação (`/api/v1/account`)

- `POST /register` - Registrar novo usuário
- `POST /login` - Autenticar e obter token JWT
- `POST /refresh` - Renovar token de acesso

### Usuários (`/api/v1/users`)

- `GET /users` - Listar usuários (com filtros e paginação)
- `GET /users/{id}` - Obter usuário por ID
- `PUT /users/{id}` - Atualizar usuário
- `DELETE /users/{id}` - Deletar usuário

### Produtos (`/api/v1/fakestoreapi`)

- `GET /fakestoreapi` - Listar todos os produtos
- `GET /fakestoreapi/{id}` - Obter produto por ID

### Favoritos (`/api/v1/favorites`)

- `GET /favorites` - Listar favoritos do usuário
- `POST /favorites` - Adicionar produto aos favoritos
- `GET /favorites/{id}` - Obter favorito por ID
- `DELETE /favorites/{id}` - Remover favorito

### Health Check

- `GET /health` - Status da API

> **Nota**: Todos os endpoints (exceto `/register` e `/login`) requerem autenticação via JWT.

## Documentação

A documentação interativa da API está disponível via Swagger UI:

```
http://localhost:8000/docs
```

Alternativamente, a documentação em formato ReDoc:

```
http://localhost:8000/redoc
```

## Conceitos Aplicados

Este projeto demonstra a aplicação prática de:

- **Clean Architecture** - Separação de responsabilidades
- **SOLID Principles** - Código extensível e manutenível
- **Design Patterns** - Cache-Aside, Repository, Use Case
- **Async/Await** - Programação assíncrona em Python
- **JWT Authentication** - Autenticação stateless
- **Database Migrations** - Versionamento de schema
- **Background Tasks** - Processamento assíncrono
- **Error Handling** - Tratamento robusto de erros
- **API Documentation** - OpenAPI/Swagger

---

Se este projeto foi útil para você, considere dar uma estrela no repositório!
