# Documentação de Testes - Issue Tracker API

Este diretório contém a suíte completa de testes automatizados para a Issue Tracker API. A suíte é composta por cerca de 200 testes, garantindo a fiabilidade, segurança e integridade das regras de negócio.

## 🛠️ Ferramentas Utilizadas
* **[Pytest](https://docs.pytest.org/)**: Framework principal para estruturação e execução dos testes.
* **[pytest-cov](https://pytest-cov.readthedocs.io/)**: Geração de relatórios de cobertura de código (*coverage*).
* **SQLite (In-Memory)**: Base de dados isolada e recriada a cada teste para garantir execução rápida e evitar poluição de estado (*Test Pollution*).

## 📁 Estrutura da Suíte de Testes

A nossa estratégia divide-se em duas camadas principais:

### 1. Testes Unitários (`tests/unit/`)
Testam a lógica de negócio isolada da camada de transporte (HTTP). Focam-se nos `Services` e garantem que as regras da aplicação funcionam independentemente das rotas.
* **`test_auth_service.py` / `test_auth_service_extra.py`**: Registo, login, encriptação de passwords, validação de tokens JWT e refresh tokens.
* **`test_project_service.py`**: Criação de projetos, gestão de permissões (Owner vs Member), atualização e deleção.
* **`test_services.py`**: Engloba a lógica de negócio para Issues, Comments e Labels. Valida a hierarquia de acessos (ex: apenas membros do projeto podem criar/comentar numa issue).
* **Testes de Utils**: Validação da estrutura de respostas da API e da mecânica de paginação.

### 2. Testes de Integração (`tests/integration/`)
Testam o fluxo completo (HTTP Request -> Route -> Service -> Repository -> In-Memory DB -> HTTP Response) usando o `test_client` do Flask.
* **`test_auth_routes.py`**: Valida os endpoints de `/api/v1/auth`, incluindo respostas de erro (400, 401).
* **`test_project_routes.py`**: Testa as rotas de projetos, incluindo paginação e injeção de metadata nas respostas.
* **`test_issue_routes.py`**: Rotas de criação de tarefas, atribuição de utilizadores (assignees) e filtros de pesquisa.
* **`test_comment_routes.py`**: Rotas de discussão dentro das issues.
* **`test_label_routes.py`**: Proteção de rotas (ex: apenas `admins` podem criar/apagar labels globais).
* **`test_health_routes.py`**: Verificação do estado da API (Health checks).

## ⚙️ Fixtures e Configuração (`conftest.py`)
O ficheiro `conftest.py` é o coração da nossa suíte de testes. Ele providencia:
* Um `app_context` do Flask configurado para modo de testes (`TESTING=True`).
* Um cliente HTTP de testes (`client`).
* Uma fixture `db` que **recria automaticamente todas as tabelas** antes de cada teste e faz um *drop* no final, garantindo 100% de isolamento.
* Utilizadores e entidades pré-construídas (`sample_user`, `admin_user`, `sample_project`, etc.) para uso rápido nas funções de teste.

## 🚀 Como Executar

**Correr todos os testes:**
```bash
pytest tests/
```

**Correr com relatório de cobertura (Coverage):**
```bash
pytest tests/ --cov=src --cov-report=term-missing
```

**Correr testes específicos:**
```bash
pytest tests/unit/test_auth_service.py
```