# Integração - Fake Store API

Este projeto foi desenvolvido com o objetivo de  implementar  uma API RESTful escalável e resiliente  que integra dados de uma API pública externa (FakeStoreAPI).
A aplicação segue princípios de baixo acoplamento, alta coesão e separação de responsabilidades para garantir.  fácil manutenção, escalabilidade horizontal e resiliência a falhas de rede ou indisponibilidade da API externa.

## Requisitos e Estratégias Adotadas

- ### Autenticação e Autorização

A autenticação é realizada via JWT, garantindo que o serviço seja Stateless  (sem estado no servidor).O sistema possui dois perfis de usuário:

- ADMIN – pode visualizar e gerenciar favoritos de todos os usuários.
- USER – pode visualizar e gerenciar apenas seus próprios favoritos.

## Performance e Escalabilidade

Para reduzir a latência e aumentar a disponibilidade, foi adotado o Redis como cache primário.O cache é utilizado em conjunto com uma estratégia de atualização assíncrona gerenciada pelo Celery, permitindo respostas imediatas mesmo quando a API externa está lenta ou indisponível.
A arquitetura do projeto é modular, seguindo o padrão Controller → Use Case → Service, o que facilita a expansão de novas funcionalidades sem impactar os módulos existentes.A separação de responsabilidades entre API, regras de negócio, tarefas assíncronas e persistência garante a possibilidade de escalar cada componente de forma independente — por exemplo:

- Aumentar réplicas do backend (FastAPI) para suportar mais requisições;
- Escalar workers Celery separadamente conforme a demanda de tarefas em background;
- Utilizar instâncias Redis e PostgreSQL distribuídas em clusters.

## Integridade dos Dados

O banco de dados foi estruturado em PostgreSQL, aplicando boas práticas de modelagem relacional e criação de índices em campos de busca para garantir eficiência nas consultas.
As relações entre entidades (usuários, produtos e favoritos) seguem regras de integridade referencial de dados.

## Estratégia de Resiliência e Cache

Para evitar quedas e garantir disponibilidade mesmo quando a API externa está fora do ar, a aplicação segue o seguinte fluxo:

1. Consulta ao Redis:
   O sistema verifica se a informação está disponível no cache.
   Os dados armazenados possuem um TTL configurável  no arquivo .env
   Se o registro ainda estiver válido, ele é retornado imediatamente ao usuário.
2. Cache ausente ou expirado:Caso o dado não esteja em cache, o sistema realiza uma requisição à FakeStoreAPI.Assim que obtém o retorno, a aplicação:

   - Atualiza o cache Redis;
   - Persiste ou atualizado o registro no PostgreSQL;
   - E executa essas tarefas de forma assíncrona, através de uma fila Celery.
3. Falha na API externa:
   Se a FakeStoreAPI estiver indisponível, o sistema faz  fallback automático para  os dados salvos localmente no PostgreSQL, garantindo que o  usuário receba uma resposta consistente.
   (Comportamento identico nos endoints /api/v1/fakestoreapi e /api/v1/fakestoreapi/{id})

## Tecnologias Utilizadas

Linguagem: Python 3.11+
Web Framework: FastAPI
Banco de Dados: PostgreSQL (Persistência síncrona e  assíncrona)
Cache: Redis (Armazenamento em memória e fila do Celery)
Fila: Celery (Execução de tarefas assíncronas )
Migrações: Alembic (Controle de versão e migrações do schema)
Documentação: Swagger

## pré-requisitos

- Instancia do banco de dados Postgres
- Instancia do Redis
- git

## Inicialização do projeto

```bash
# Baixar o código fonte 
$ git clone git@github.com:ivancley/fakestoreapi-fastapi.git
$ cd fakestoreapi-fastapi
```

```bash
# Criar ambiente virtual
$ python3 -m venv .venv

# Ativa o ambiente virtual
$ source .venv/bin/activate

# Instalar as dependências
$ pip install -r requirements.txt
```

Criar uma cópia do arquivo .env_example, renomear para .env e atualizar as variáveis de ambiente.

```bash
# Rodar as Migrações
$ alembic upgrade head

# Subir o Celery 
$ celery -A api.utils.celery worker --loglevel=info  

# Subir o Servidor 
$ uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Criar o primeiro usuário do sistema

```bash
$ python3 create_inicial_user.py
```

## Swagger 
O Swagger exibirá todos os endpoints
```bash 
http://localhost:8000/docs
``` 
