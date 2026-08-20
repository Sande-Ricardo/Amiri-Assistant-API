# Project State

## Sprint 1: Foundation & Base Architecture
- [x] Initialize repository and configure linters (Ruff, Mypy).
- [x] Initialize FastAPI base architecture & directories structure.
- [x] Configure automated documentation via OpenAPI.
- [x] Configure Database Connection (Aiven MySQL + SSL) and SQLAlchemy Engine.
- [x] Set up Alembic and create initial migration scripts.

## Sprint 2: Persistence Layer
- [x] Create SQLAlchemy Models (`requests`, `proposals`, `agent_execution_logs`).
- [x] Implement `ProposalRepository` port adapter (MySQL).
- [x] Implement `AgentLogRepository` port adapter (MySQL).

## Sprint 3: LLM Provider & Agent Prompts Layer
- [x] Implement LLM Provider Strategy (Gemini / Groq selection via Factory).
- [x] Define LLM Input/Output Pydantic Schemas (AnalystOutputSchema, ArchitectOutputSchema).
- [x] Develop Analyst Agent logic & prompts (Requirement extraction & ambiguity detection).
- [ ] Develop Architect Agent logic & prompts (Module definition, hour estimation, assumption resolution).
- [ ] Develop Writer Agent logic & prompts (Markdown compilation).

## Sprint 4: LangGraph Orchestration & API Integration
- [ ] Define LangGraph `ProposalGenerationState` (TypedDict).
- [ ] Implement LangGraph nodes and conditional edges (DAG pipeline).
- [ ] Integrate LangGraph execution with FastAPI `BackgroundTasks`.
- [ ] Connect `POST /api/v1/proposals/generate` to trigger the pipeline.
- [ ] Connect `GET /api/v1/proposals/{id}/status` to fetch real-time state and final markdown.

## Sprint 5: Testing, Resilience, & Deployment
- [ ] Implement Error Handling & LLM Retry mechanism (Rate limits, Fallbacks).
- [ ] Write Unit Tests for individual Agent Nodes (mocking LLM).
- [ ] Write Integration Tests for FastAPI Endpoints.
- [ ] Finalize Render/Railway Deployment Configuration.

## Blockers
- None.

## Notes
- Database credentials pending from DevOps. Mock data for now.
