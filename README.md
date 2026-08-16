# Amiri - Automated B2B Commercial Proposal Generator

**Project Code:** GAPC-B2B
**Version:** 1.0.0
**Status:** Approved for development

## Description

Amiri is a backend system that receives unstructured commercial requirements (free text) from prospective clients and, through a multi-agent architecture orchestrated with LangGraph, autonomously produces a formal commercial proposal in Markdown format. The system runs a sequential pipeline of three specialized agents (Analyst, Architect, Writer) that extract requirements, infer a technical solution, and compile a final document ready to be delivered to the client.

**Scope - Included:**

- Backend REST API (FastAPI)
- Multi-agent orchestration (LangGraph)
- Persistence in MySQL (Aiven Free Tier)
- Integration with a free LLM (Google Gemini 1.5 Flash / Groq Llama 3)
- Deployment specification on Render/Railway Free Tier

**Scope - Excluded:**

- Frontend / user interface (Next.js or any other framework)
- End-user authentication via UI
- Billing or payment gateways
- Any client-side visual rendering logic

---

## Architecture Overview

The system follows a **Hexagonal Architecture (Ports & Adapters)** combined with a **Directed Acyclic Graph (DAG)** style agent orchestration.

### Design Patterns

| Pattern | Justification |
|---|---|
| Sequential DAG | The agent pipeline (Analyst -> Architect -> Writer) does not require review cycles; each node consumes the state enriched by the previous one and never returns to a prior node. |
| Repository Pattern | Abstracts MySQL access through repositories (`RequestRepository`, `ProposalRepository`, `AgentLogRepository`) to decouple business logic from the ORM. |
| Dependency Injection | FastAPI `Depends()` is used to inject database sessions, LLM clients, and orchestration services into the endpoints. |
| Asynchronous Task Processing (Fire-and-Forget with polling) | Since generating the proposal through three sequential LLM calls can exceed a synchronous HTTP request timeout, execution happens in the background via FastAPI `BackgroundTasks`, avoiding paid infrastructure dependencies such as Redis/Celery. |
| State Pattern (LangGraph State) | The shared state (`TypedDict`) acts as a mutable working memory that flows through the graph nodes. |
| Strategy Pattern for the LLM provider | Abstraction over the LLM provider (Gemini or Groq) via a common interface, allowing the provider to be switched through an environment variable without modifying the agent nodes. |
| Fail-Fast with propagated error state | On an unrecoverable failure in any node, the graph short-circuits execution via a conditional edge to `END` instead of continuing with incomplete data. |

### Main Components

| Component | Responsibility |
|---|---|
| API Layer (FastAPI) | Expose REST endpoints, validate payloads with Pydantic, delegate generation to the orchestration layer, and persist results. |
| Orchestration Layer (LangGraph) | Execute the agent graph sequentially, manage the shared state, and handle errors per node. |
| Agents Layer | Contains the logic, prompts, and validation schemas for the three agents: Analyst, Architect, and Writer. |
| Persistence Layer (SQLAlchemy + MySQL) | Store the request history, intermediate results, and final proposals in Aiven MySQL. |
| LLM Provider Layer | Encapsulates calls to Google Gemini 1.5 Flash or Groq Llama 3 via LangChain, including retries and free-tier rate-limit control. |
| Background Executor | Runs the LangGraph pipeline asynchronously after responding `202 Accepted` to the client. |

### General Flow

1. The client sends a `POST` request with the raw text of the requirement.
2. The API creates a record in the `requests` table with `status='pending'`, returns a `request_id` and `202 Accepted`, and launches the LangGraph execution as a background task.
3. The graph runs sequentially: `analyst_agent -> architect_agent -> writer_agent`, with no review cycles.
4. Each node updates the shared state and persists a row in `agent_execution_logs`.
5. On success, the record in `requests` is updated to `status='completed'` and a row is inserted into `proposals` with the final Markdown.
6. The client polls `GET /status/{id}` until it receives `status='completed'` or `status='failed'`.

---

## Core Workflow (The Agents)

The orchestration layer executes a strictly sequential DAG with no review cycles, defined via LangGraph `StateGraph`, using a shared `ProposalGenerationState` (`TypedDict`).

### 1. Analyst Agent (`analyst_agent`)

Structurally extracts the explicit and implicit functional and non-functional requirements contained in the client's raw text, and exhaustively detects every ambiguity, information gap, or contradiction that could impact the design of the solution. It does not propose technical solutions or technologies; that responsibility belongs to the Architect Agent.

- **LLM temperature:** 0.2 (maximum extraction consistency)
- **Input state keys:** `raw_requirements`, `client_name`
- **Output state keys:** `clean_requirements`, `identified_ambiguities`, `current_stage`
- **Notes:** `raw_requirements` is sanitized before invoking the LLM (trim, configurable length limit, removal of possible instruction override patterns). The response is validated against `AnalystOutputSchema`; on validation failure, it is retried once with a correction prompt.

### 2. Architect Agent (`architect_agent`)

Designs the technical solution at a high level: defines the functional modules of the proposed system, estimates development hours per module, suggests a reasonable tech stack when the client did not specify one, and resolves each ambiguity detected by the Analyst Agent through an explicit, justified assumption, without halting the pipeline.

- **LLM temperature:** 0.4 (balance between technical creativity and consistency)
- **Input state keys:** `clean_requirements`, `identified_ambiguities`
- **Output state keys:** `proposed_modules`, `suggested_tech_stack`, `resolved_assumptions`, `total_estimated_hours`, `current_stage`
- **Notes:** `total_estimated_hours` is recalculated and validated in code by summing `estimated_hours` across all `proposed_modules`, rather than trusting the value returned directly by the LLM.

### 3. Writer Agent (`writer_agent`)

Compiles all information generated by the previous agents into a final commercial proposal document, formal, persuasive, and well-structured, in Markdown format, ready to be delivered directly to the client.

- **LLM temperature:** 0.6 (greater narrative fluency and commercial tone)
- **Input state keys:** `client_name`, `clean_requirements`, `proposed_modules`, `suggested_tech_stack`, `resolved_assumptions`, `total_estimated_hours`
- **Output state keys:** `final_markdown_proposal`, `current_stage`
- **Mandatory document sections (in order):** `# Commercial Proposal`, `## Executive Summary`, `## Understanding of the Requirement`, `## Proposed Solution` (with subsections per module), `## Suggested Tech Stack`, `## Hour Estimate and Timeline`, `## Assumptions and Clarifications`, `## Next Steps`.
- **Notes:** The output is stored as-is in `proposals.final_markdown`; no post-processing is applied beyond `trim()` and verifying the document is not empty. On successful completion, `requests.status` is updated to `completed`.

### Graph Edges

- Type: Strictly sequential DAG, with no review cycles.
- Entry point: `analyst_agent`.
- `START -> analyst_agent` (unconditional).
- `analyst_agent -> architect_agent` if `state.error_log is None`, otherwise `-> END`.
- `architect_agent -> writer_agent` if `state.error_log is None`, otherwise `-> END`.
- `writer_agent -> END` (unconditional).
- **Checkpointer:** Not required for v1.0.0 (single-shot execution); progress is reflected directly in the `requests` table via `current_node`. LangGraph's `MemorySaver` may be added in a future phase if resuming interrupted executions is required.

---

## Tech Stack

| Category | Technology |
|---|---|
| Language | Python 3.11+ |
| API Framework | FastAPI ^0.115.0, served via Uvicorn (standard worker; no multiple workers on Free Tier due to RAM limits) |
| AI Framework | LangGraph ^0.2.0, with LangChain Core ^0.3.0 for message abstractions, prompts, and structured parsers |
| LLM Provider (primary) | Google Gemini 1.5 Flash, via `langchain-google-genai` (Google AI Studio Free Tier) |
| LLM Provider (alternative) | Groq (Llama 3.1 8B Instant / Llama 3 70B), via `langchain-groq` (Groq Cloud Free Tier), used as a fallback if Gemini hits its rate limit |
| Database | MySQL 8.0, hosted on Aiven for MySQL (Free Tier) |
| ORM | SQLAlchemy 2.x (declarative mode + Core for complex queries) |
| DB Driver | PyMySQL |
| Migrations | Alembic |
| Data Validation | Pydantic v2 |
| Configuration Management | pydantic-settings (typed environment variable loading) |
| Testing | pytest, pytest-asyncio, httpx (`AsyncClient`) |
| Structured Logging | Python standard `logging` with JSON format (or `structlog`), correlated by `request_id` |
| Hosting | Render (Free Tier - Web Service), alternatively Railway (Free Tier) |

The LLM provider is selected via the `LLM_PROVIDER` environment variable (`'gemini'` or `'groq'`), resolved by a Factory in the LLM provider layer.

---

## Getting Started

### Prerequisites

- Python 3.11 or higher.
- A MySQL 8.0 instance (Aiven for MySQL Free Tier is the recommended hosting option). SSL/TLS connection is required.
- An API key for at least one LLM provider:
  - Google AI Studio API key (for `GOOGLE_API_KEY`, if using Gemini), and/or
  - Groq Cloud API key (for `GROQ_API_KEY`, if using Groq).

### Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | Yes | - | Full connection string to Aiven MySQL. Format: `mysql+pymysql://user:password@host:port/db_name`. Example: `mysql+pymysql://avnadmin:xxxxx@mysql-xxxx.aivencloud.com:12345/defaultdb` |
| `DB_SSL_CA_PATH` | Yes | - | Path to the CA certificate downloaded from the Aiven console, required for the mandatory SSL connection. |
| `LLM_PROVIDER` | Yes | `gemini` | Selector for the active LLM provider. Valid values: `gemini` \| `groq`. |
| `GOOGLE_API_KEY` | No | - | Google AI Studio API Key, required if `LLM_PROVIDER=gemini`. |
| `GROQ_API_KEY` | No | - | Groq Cloud API Key, required if `LLM_PROVIDER=groq`. |
| `GEMINI_MODEL_NAME` | No | `gemini-1.5-flash` | Name of the Gemini model to use. |
| `GROQ_MODEL_NAME` | No | `llama-3.1-8b-instant` | Name of the Groq model to use. |
| `PORT` | Yes | - | Port automatically injected by Render/Railway; Uvicorn must bind to `0.0.0.0:$PORT`. |
| `ENVIRONMENT` | No | `production` | Runtime environment identifier. |
| `LOG_LEVEL` | No | `INFO` | Application log level. |
| `CORS_ALLOWED_ORIGINS` | Yes | - | Comma-separated list of allowed origins (frontend domain, managed outside this scope). |
| `MAX_LLM_RETRIES` | No | `2` | Number of retries on LLM provider error or rate-limit before marking the request as `failed`. |
| `REQUEST_TIMEOUT_SECONDS` | No | `120` | Maximum timeout for the full 3-agent pipeline execution. |

### Installation & Execution

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Configure the environment variables listed above (for example, using a `.env` file loaded via `python-dotenv` / `pydantic-settings`).

3. Apply database migrations (run as a release step before service startup):

   ```bash
   alembic upgrade head
   ```

4. Start the API server:

   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

**Key `requirements.txt` dependencies:**

```
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
langgraph>=0.2.0
langchain-core>=0.3.0
langchain-google-genai>=2.0.0
langchain-groq>=0.2.0
sqlalchemy>=2.0.0
pymysql>=1.1.0
alembic>=1.13.0
pydantic>=2.8.0
pydantic-settings>=2.4.0
python-dotenv>=1.0.0
cryptography>=42.0.0
```

---

## API Reference

Base path: `/api/v1`

### `POST /api/v1/proposals/generate`

Receives the client's unstructured requirement text, creates a request record with `status='pending'`, and triggers the asynchronous execution of the LangGraph agent graph in the background via `BackgroundTasks`. Responds immediately without waiting for the pipeline to finish.

**Request body** (`application/json`):

| Field | Type | Required | Description |
|---|---|---|---|
| `raw_requirements` | string | Yes | Free text with the client's requirements. Minimum length: 20 characters. |
| `client_name` | string | No | Client or company name, optional. |

Example request:

```json
{
  "raw_requirements": "We need a system to manage our online store's inventory, with monthly reports and notifications when stock is low.",
  "client_name": "Comercial Andina S.A."
}
```

**Success response - `202 Accepted`:**

```json
{
  "request_id": "string (uuid)",
  "status": "pending",
  "status_check_url": "/api/v1/proposals/{request_id}/status",
  "created_at": "string (ISO 8601)"
}
```

**Error responses:**

| Code | Description |
|---|---|
| 422 | Invalid payload (Pydantic validation failed, e.g. `raw_requirements` empty or too short). |
| 500 | Internal error while creating the record in the database. |

### `GET /api/v1/proposals/{request_id}/status`

Allows polling the current status of a request. If the status is `completed`, the response includes the final proposal in Markdown and the metadata generated by each agent. A polling interval of 3 to 5 seconds from the consuming client is recommended.

**Path parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `request_id` | string (uuid) | Yes | Identifier of the request to poll. |

**Success response - `200 OK`:**

```json
{
  "request_id": "string (uuid)",
  "status": "pending | processing | completed | failed",
  "current_node": "string | null",
  "proposal": {
    "final_markdown": "string",
    "total_estimated_hours": 0,
    "suggested_tech_stack": {},
    "identified_ambiguities": [],
    "resolved_assumptions": []
  },
  "error_message": "string | null",
  "created_at": "string (ISO 8601)",
  "updated_at": "string (ISO 8601)"
}
```

Notes:
- `current_node` reflects the executing node (e.g. `architect_agent`), useful for showing granular progress.
- `proposal` is only present when `status='completed'`.
- `error_message` is present only when `status='failed'`.

**Error responses:**

| Code | Description |
|---|---|
| 404 | No request exists with the provided `request_id`. |

Real-time update mechanism: this endpoint uses **polling** as the primary strategy. A future alternative, out of scope for v1.0.0, is Server-Sent Events (SSE) at `/api/v1/proposals/{request_id}/stream`.

### `GET /health`

Service health-check endpoint, used by Render/Railway for automated health checks. Verifies MySQL connectivity.

**Success response - `200 OK`:**

```json
{
  "status": "ok",
  "database": "connected | disconnected"
}
```

---

## Deployment

Supported platforms:

- **Render** (Free Tier - Web Service) - recommended.
- **Railway** (Free Tier) - alternative.

**Build command:**

```bash
pip install -r requirements.txt
```

**Start command:**

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Migrations** (run as a release step before service startup):

```bash
alembic upgrade head
```

### Free Tier Considerations

- Both Render and Railway Free Tier plans suspend the service after inactivity, causing a cold start of up to 30-50 seconds on the next request. The asynchronous design with polling (`202 Accepted` plus `GET /status`) prevents this cold start from causing a client-side timeout.
- Aiven Free Tier for MySQL has a storage limit (approximately 1 GB) and a limit on concurrent connections; a reduced connection pool (`pool_size=5`) in SQLAlchemy is recommended.
- Gemini and Groq free rate limits (requests per minute) must be handled with exponential backoff in the LLM provider layer.
- Celery combined with Redis is not recommended, since both would require additional paid infrastructure; FastAPI's `BackgroundTasks` is sufficient for the expected volume at this stage.
- No formal SLA is guaranteed given the use of Free Tier infrastructure; this is documented as a known project limitation.

The `/health` endpoint is used by Render/Railway for automated health checks and verifies MySQL connectivity before returning `200 OK`.