from fastapi import APIRouter

from app.agents.workflow import DEFAULT_WORKFLOW, run_workflow
from app.models.schemas import WorkflowConfig, WorkflowRun

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/run", response_model=WorkflowRun)
async def run_agent_workflow(user_input: str, config: WorkflowConfig | None = None):
    workflow = config or DEFAULT_WORKFLOW
    result = run_workflow(workflow, user_input)
    return result


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
