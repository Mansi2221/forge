import time
import uuid
from typing import Any

import anthropic

from app.core.config import settings
from app.models.schemas import (
    AgentConfig,
    AgentMessage,
    AgentRole,
    LLMProvider,
    WorkflowConfig,
    WorkflowRun,
)

ROLE_SYSTEM_PROMPTS = {
    AgentRole.PLANNER: (
        "You are a Planning Agent. Break down the user's request into clear, actionable steps. "
        "Output a numbered plan. Be specific and thorough."
    ),
    AgentRole.RESEARCHER: (
        "You are a Research Agent. Given a task, gather relevant information, analyze it, "
        "and provide a comprehensive summary. Use the context provided."
    ),
    AgentRole.EXECUTOR: (
        "You are an Execution Agent. Take the plan and research provided, then produce "
        "the final deliverable. Be precise and complete."
    ),
    AgentRole.REVIEWER: (
        "You are a Review Agent. Evaluate the output for correctness, completeness, "
        "and quality. Point out any issues and suggest improvements. "
        "Rate the output on a scale of 1-10."
    ),
}


def call_llm(
    model: LLMProvider,
    system_prompt: str,
    messages: list[dict],
    temperature: float = 0.7,
    max_tokens: int = 1024,
) -> tuple[str, dict]:
    if model == LLMProvider.CLAUDE:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        response = client.messages.create(
            model="claude-sonnet-5-5",
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=messages,
        )
        return response.content[0].text, {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        }
    else:
        return f"[{model.value} provider not configured — using mock response]", {
            "input_tokens": 0,
            "output_tokens": 0,
        }


def run_agent(
    agent: AgentConfig,
    task: str,
    context: str = "",
) -> AgentMessage:
    system_prompt = agent.system_prompt or ROLE_SYSTEM_PROMPTS.get(agent.role, "You are a helpful AI assistant.")
    user_content = task
    if context:
        user_content = f"Previous context:\n{context}\n\nCurrent task:\n{task}"

    response_text, usage = call_llm(
        model=agent.model,
        system_prompt=system_prompt,
        messages=[{"role": "user", "content": user_content}],
        temperature=agent.temperature,
    )

    return AgentMessage(
        role=agent.role.value,
        content=response_text,
        agent=f"{agent.role.value}_{agent.model.value}",
        metadata={"token_usage": usage, "model": agent.model.value},
    )


def run_workflow(config: WorkflowConfig, user_input: str) -> WorkflowRun:
    run_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    messages: list[AgentMessage] = []
    total_tokens: dict[str, int] = {"input": 0, "output": 0}

    messages.append(AgentMessage(
        role="user",
        content=user_input,
        agent="user",
    ))

    accumulated_context = f"User request: {user_input}"

    for agent_config in config.agents:
        agent_msg = run_agent(
            agent=agent_config,
            task=user_input,
            context=accumulated_context,
        )
        messages.append(agent_msg)

        usage = agent_msg.metadata.get("token_usage", {})
        total_tokens["input"] += usage.get("input_tokens", 0)
        total_tokens["output"] += usage.get("output_tokens", 0)

        accumulated_context += f"\n\n[{agent_config.role.value} output]:\n{agent_msg.content}"

    duration = int((time.time() - start_time) * 1000)
    final_result = messages[-1].content if messages else ""

    return WorkflowRun(
        id=run_id,
        workflow_name=config.name,
        status="completed",
        messages=messages,
        result=final_result,
        duration_ms=duration,
        token_usage=total_tokens,
    )


DEFAULT_WORKFLOW = WorkflowConfig(
    name="plan-research-execute-review",
    description="A 4-agent pipeline: planner breaks down the task, researcher gathers info, executor produces output, reviewer validates quality.",
    agents=[
        AgentConfig(role=AgentRole.PLANNER),
        AgentConfig(role=AgentRole.RESEARCHER),
        AgentConfig(role=AgentRole.EXECUTOR),
        AgentConfig(role=AgentRole.REVIEWER),
    ],
)
