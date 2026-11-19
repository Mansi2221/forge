import logging

import anthropic
from fastapi import APIRouter, HTTPException

from app.agents.workflow import DEFAULT_WORKFLOW, run_workflow
from app.models.schemas import WorkflowConfig, WorkflowRun

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/run", response_model=WorkflowRun)
async def run_agent_workflow(user_input: str, config: WorkflowConfig | None = None):
    if not user_input.strip():
        raise HTTPException(status_code=400, detail="user_input cannot be empty")
    if len(user_input) > 50000:
        raise HTTPException(status_code=400, detail="user_input exceeds maximum length")
    try:
        workflow = config or DEFAULT_WORKFLOW
        result = run_workflow(workflow, user_input)
        return result
    except anthropic.APITimeoutError:
        raise HTTPException(status_code=504, detail="LLM request timed out")
    except anthropic.RateLimitError:
        raise HTTPException(status_code=429, detail="LLM rate limit exceeded")
    except anthropic.APIError as e:
        logger.error("Agent workflow failed: %s", e.message)
        raise HTTPException(status_code=502, detail="LLM service error")


@router.get("/workflows")
async def list_workflows():
    return {
        "workflows": [
            {
                "name": DEFAULT_WORKFLOW.name,
                "description": DEFAULT_WORKFLOW.description,
                "agents": [a.role.value for a in DEFAULT_WORKFLOW.agents],
            }
        ]
    }
