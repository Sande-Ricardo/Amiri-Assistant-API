from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

TAGS_METADATA: list[dict[str, Any]] = [
    {
        "name": "Health",
        "description": "System operational status and database connectivity checks.",
    },
    {
        "name": "Proposals",
        "description": (
            "Commercial proposal generation pipeline endpoints. Supports "
            "asynchronous initiation via 202 Accepted and real-time status polling."
        ),
    },
]

OPENAPI_DESCRIPTION = """
### Amiri - Automated B2B Commercial Proposal Generator API

Amiri is an autonomous backend service that processes unstructured commercial requirements 
from prospective clients and compiles formal, persuasive B2B proposals in Markdown format.

#### Key Architectural Highlights
* **Multi-Agent Pipeline**: Orchestrated using a sequential Directed Acyclic Graph (DAG) with LangGraph (Analyst -> Architect -> Writer).
* **Asynchronous Execution**: Asynchronous processing via FastAPI `BackgroundTasks` with status polling endpoints.
* **Hexagonal Architecture**: Strict separation of concerns (Ports, Adapters, Domain, API, Orchestration).
"""


def custom_openapi_generator(app: FastAPI) -> dict[str, Any]:
    """Generates and caches custom OpenAPI schema for the application."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Amiri B2B Proposal Generator API",
        version="1.0.0",
        description=OPENAPI_DESCRIPTION,
        routes=app.routes,
        tags=TAGS_METADATA,
    )

    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema
