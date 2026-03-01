Relatório Técnico: Issue Tracker API
Autor: Mário Prazeres
Repositório: MPrazeres-1983/issue-tracker-api

1. Resumo Executivo
O Issue Tracker API é uma interface de programação de aplicações (API) RESTful desenvolvida em Python. O sistema tem como objetivo o fornecimento de um motor robusto para a gestão de projetos, rastreamento de tarefas (issues), comentários e etiquetas (labels). Foi desenhado com um foco rigoroso na escalabilidade, segurança e testabilidade, simulando os requisitos de um ambiente de produção empresarial.

2. Arquitetura do Sistema e Padrões de Design
O projeto foi estruturado utilizando uma arquitetura em camadas (Layered Architecture), promovendo o princípio da Separação de Preocupações (Separation of Concerns). Esta abordagem garante que o código é modular, testável e fácil de manter.

O sistema divide-se nas seguintes camadas:

Rotas / Controladores (src/routes/): Camada de apresentação que lida com os pedidos HTTP, extração de parâmetros e injeção de dependências.

Serviços (src/services/): O núcleo da aplicação (Core Business Logic). Encapsula todas as regras de negócio e validações de autorização (ex: garantir que apenas um membro de um projeto pode comentar numa issue).

Repositórios (src/repositories/): Implementação do Repository Pattern. Abstrai a base de dados, permitindo que os Serviços interajam com os dados sem conhecerem a linguagem SQL ou detalhes do ORM.

Modelos (src/models/): Representação das entidades da base de dados (Users, Projects, Issues, Comments, Labels) e dos seus relacionamentos.

Schemas (src/schemas/): Camada de serialização e validação de dados de entrada/saída utilizando a biblioteca Marshmallow.

3. Stack Tecnológica
Linguagem: Python 3.13+

Framework Web: Flask (escolhido pela sua leveza e flexibilidade na construção de microserviços).

Base de Dados e ORM: PostgreSQL (via SQLAlchemy) para persistência relacional complexa.

Autenticação: JWT (JSON Web Tokens) com implementação de Controlo de Acessos Baseado em Funções (Role-Based Access Control - RBAC), distinguindo administradores, developers, donos de projetos e membros.

Logs Estruturados: Implementação de python-json-logger para facilitar a ingestão de logs por ferramentas de observabilidade (ex: ELK Stack ou Datadog).

4. Garantia de Qualidade e CI/CD
Um dos maiores destaques deste projeto é a sua robusta infraestrutura de testes e integração contínua:

Testes Automatizados: Suíte abrangente com cerca de 200 testes (unitários e de integração), utilizando pytest.

Isolamento de Estado (Test Pollution Mitigation): Configuração avançada de fixtures que utiliza bases de dados SQLite in-memory, recriando e destruindo tabelas dinamicamente a cada teste, garantindo 100% de isolamento entre execuções.

Cobertura de Código (Coverage): +75% de cobertura validada.

Pipeline CI/CD (GitHub Actions): Automação de testes em cada push/pull request, assegurando que nenhum código quebrado é integrado na ramificação principal. Integração com o Codecov para auditoria visual da cobertura de testes.