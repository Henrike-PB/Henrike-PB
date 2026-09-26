<h1 align="center">Henrike Pajares Braga</h1>

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=500&size=20&duration=2800&pause=900&color=017CEE&center=true&vCenter=true&width=620&lines=%24+airflow+dags+trigger+henrike_profile;Engenheiro+de+Dados+I+na+Appmax;Python+%C2%B7+SQL+%C2%B7+Airflow+%C2%B7+AWS+%C2%B7+LLMs;state%3A+running+%E2%96%B6" alt="$ airflow dags trigger henrike_profile">
</p>

<p align="center">
  <a href="https://www.linkedin.com/in/henrikebraga/">LinkedIn</a> ·
  <a href="https://henrike-pb.github.io">Portfólio</a> ·
  <a href="mailto:pajaresbragahenrike@gmail.com">E-mail</a>
</p>

## ▶ DAG run: `henrike_profile`

Atuo nos projetos de dados da Appmax: serviços backend em Python, fluxos orientados a eventos na AWS, integrações com parceiros e LLMs, e a camada de dados que sustenta esses produtos.

```text
[2026-09-26 09:00:00] INFO  dag_id=henrike_profile      state=running
[2026-09-26 09:00:01] INFO  task=extract_experience     "Engenheiro de Dados I · Appmax"
[2026-09-26 09:00:02] INFO  task=extract_education      "ADS · UNISINOS  |  alumni Geração Caldeira"
[2026-09-26 09:00:03] INFO  task=transform_skills       [serviços de dados, event-driven, integrações, LLMs]
[2026-09-26 09:00:04] WARN  task=learning               backlog=5 livros + trilhas  (ver learning_pipeline ↓)
[2026-09-26 09:00:05] INFO  task=load_career            proximo_passo="pleno"  state=queued
```

## 🔁 Graph view: `carreira`

```mermaid
flowchart LR
  W["dev_web_fullstack<br/>IOS 2023-24"] --> A["caldeira_python<br/>2024"]
  A --> B["assistente_eng_dados<br/>2025"]
  B --> C["engenheiro_dados_i<br/>2026"]
  C --> D["engenheiro_dados_pleno"]
  D --> E["engenheiro_dados_senior"]
  classDef success fill:#1a7f37,stroke:#1a7f37,color:#ffffff
  classDef running fill:#9a6700,stroke:#9a6700,color:#ffffff
  classDef queued fill:#57606a,stroke:#57606a,color:#ffffff
  class W,A,B success
  class C running
  class D,E queued
```

<sub>🟩 success · 🟨 running · ⬜ queued</sub>

## 🧩 Tasks

| task_id | o que faz |
|---|---|
| `data_services` | Serviços backend e APIs em Python que sustentam produtos de dados |
| `event_driven` | Fluxos assíncronos com Lambda, SQS, SNS e EventBridge: filas, DLQ e reprocessamento |
| `integrations` | Integrações com parceiros e APIs externas, como a WhatsApp Business Platform da Meta |
| `llm_flows` | Fluxos que integram LLMs, com dados e contexto confiáveis |
| `data_layer` | Modelagem, migrations e camadas de serving em PostgreSQL, Redis e Redshift |
| `pipelines` | ETL com PySpark e Airflow, do data lake ao data warehouse |
| `operate` | Investigação de incidentes, post-mortems e documentação dos fluxos que construo |
| `ship` | Infraestrutura como código, containers e CI/CD com gates de segurança |

## 🗂️ Data catalog

```sql
SELECT camada, ferramentas FROM henrike.stack ORDER BY camada;
```

| camada | | ferramentas |
|---|---|---|
| `linguagens` | <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@v2.17.0/icons/python/python-original.svg" height="28" alt="python"> | Python · SQL |
| `backend_python` | <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@v2.17.0/icons/fastapi/fastapi-original.svg" height="28" alt="fastapi"> <img src="https://cdn.simpleicons.org/pydantic" height="28" alt="pydantic"> <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@v2.17.0/icons/sqlalchemy/sqlalchemy-original.svg" height="28" alt="sqlalchemy"> <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@v2.17.0/icons/pytest/pytest-original.svg" height="28" alt="pytest"> | FastAPI · Pydantic · SQLAlchemy · Alembic · pytest |
| `aws` | <img src="https://skillicons.dev/icons?i=aws" height="28" alt="aws"> | Lambda · SQS · SNS · EventBridge · API Gateway · S3 · EC2 · ECS Fargate · CloudWatch |
| `bancos_de_dados` | <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@v2.17.0/icons/postgresql/postgresql-original.svg" height="28" alt="postgresql"> <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@v2.17.0/icons/redis/redis-original.svg" height="28" alt="redis"> <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@v2.17.0/icons/dynamodb/dynamodb-original.svg" height="28" alt="dynamodb"> <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@v2.17.0/icons/mysql/mysql-original.svg" height="28" alt="mysql"> | RDS / Aurora PostgreSQL · Redshift · DynamoDB · Redis · MySQL |
| `processamento` | <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@v2.17.0/icons/apachespark/apachespark-original.svg" height="28" alt="apachespark"> <img src="https://cdn.simpleicons.org/databricks" height="28" alt="databricks"> <img src="https://cdn.simpleicons.org/pandas/150458/ffffff" height="28" alt="pandas"> | PySpark · Databricks · Pandas · EMR Serverless |
| `orquestracao` | <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@v2.17.0/icons/apacheairflow/apacheairflow-original.svg" height="28" alt="apacheairflow"> | Airflow |
| `integracoes_ia` | <img src="https://cdn.simpleicons.org/whatsapp" height="28" alt="whatsapp"> <img src="https://cdn.simpleicons.org/meta" height="28" alt="meta"> | WhatsApp Business API (Meta) · REST · Webhooks · LLMs |
| `devops` | <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@v2.17.0/icons/terraform/terraform-original.svg" height="28" alt="terraform"> <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@v2.17.0/icons/docker/docker-original.svg" height="28" alt="docker"> <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@v2.17.0/icons/gitlab/gitlab-original.svg" height="28" alt="gitlab"> <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@v2.17.0/icons/git/git-original.svg" height="28" alt="git"> <img src="https://cdn.simpleicons.org/trivy" height="28" alt="trivy"> | Terraform · Docker · GitLab CI · Trivy · Git |
| `ferramentas` | <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@v2.17.0/icons/vscode/vscode-original.svg" height="28" alt="vscode"> <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@v2.17.0/icons/datagrip/datagrip-original.svg" height="28" alt="datagrip"> <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@v2.17.0/icons/jupyter/jupyter-original.svg" height="28" alt="jupyter"> | VS Code · DataGrip · Jupyter |

<sub>(9 rows)</sub>

## 📚 Backlog: `learning_pipeline`

<sub><code>schedule="um livro por vez"</code> · cada leitura roda em paralelo com uma trilha de cursos da mesma área · clique no título para ver o livro</sub>

| janela | livro | trilha em paralelo | state |
|---|---|---|---|
| out–nov 2026 | [Fundamentos de Engenharia de Dados](https://www.amazon.com.br/Fundamentos-Engenharia-Dados-Construa-Sistemas/dp/8575228765) (Reis & Housley) | Orquestração com Airflow | ⏭️ next |
| dez 2026–jan 2027 | [Arquitetura Limpa](https://www.amazon.com.br/Arquitetura-Limpa-Artes%C3%A3o-Estrutura-Software/dp/8550804606) (Robert C. Martin) | Python avançado, testes e SOLID | ⬜ queued |
| fev–abr 2027 | [Projetando Aplicações com Uso Intensivo de Dados, 2ª ed.](https://www.amazon.com.br/Projetando-Aplica%C3%A7%C3%B5es-com-Intensivo-Dados/dp/6583913062) (Kleppmann & Riccomini) | PostgreSQL, mensageria e microsserviços | ⬜ queued |
| mai–jun 2027 | [Padrões de Design de Engenharia de Dados](https://www.amazon.com.br/Padr%C3%B5es-Design-Engenharia-Dados-engenharia/dp/8575229664) (Konieczny) | FastAPI e padrões de API HTTP | ⬜ queued |
| jul–set 2027 | [Engenharia de IA](https://www.amazon.com.br/Engenharia-IA-Construindo-aplica%C3%A7%C3%B5es-funda%C3%A7%C3%A3o/dp/8575229966) (Chip Huyen) | Agentes de IA e MCP | ⬜ queued |
| contínuo | — | Docker, observabilidade, OpenTelemetry e inglês técnico | 🟨 running |
| 2027 | — | Certificação AWS (em preparação) | 🟨 running |

## 🎓 Formação

```sql
SELECT curso, instituicao, periodo FROM henrike.formacao ORDER BY inicio;
```

| curso | instituição | período |
|---|---|---|
| Desenvolvimento Web Full Stack | Instituto da Oportunidade Social (atual Instituto Percorre) | ✅ 2023–2024 |
| Geração Caldeira, trilha Python | Instituto Caldeira | ✅ 2024 · alumni |
| Análise e Desenvolvimento de Sistemas | UNISINOS | 🔄 cursando |

<sub>(3 rows)</sub>

---

```text
$ airflow dags trigger henrike_profile --conf '{"visitante": "você"}'
[INFO] task=register_visit     state=success
[INFO] Marking run as SUCCESS. Obrigado pela visita! 👋
```

<p align="center">
  <img src="https://komarev.com/ghpvc/?username=Henrike-PB&label=visitantes%20processados&color=017CEE&style=flat-square" alt="visitantes processados">
  <img src="https://img.shields.io/badge/dag__status-success-1a7f37?style=flat-square" alt="dag_status: success">
  <img src="https://img.shields.io/github/last-commit/Henrike-PB/Henrike-PB?label=last_run&style=flat-square&color=1a7f37" alt="última execução">
</p>
