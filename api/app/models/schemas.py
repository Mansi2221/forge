from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class LLMProvider(str, Enum):
    CLAUDE = "claude"
    GPT = "gpt"
    GEMINI = "gemini"


class AgentRole(str, Enum):
    PLANNER = "planner"
    RESEARCHER = "researcher"
    EXECUTOR = "executor"
    REVIEWER = "reviewer"


class GuardrailType(str, Enum):
    PROMPT_INJECTION = "prompt_injection"
    PII_DETECTION = "pii_detection"
    HALLUCINATION = "hallucination"
    TOXICITY = "toxicity"


# --- Agent Schemas ---


class AgentConfig(BaseModel):
    role: AgentRole
    model: LLMProvider = LLMProvider.CLAUDE
    system_prompt: str = ""
    tools: list[str] = Field(default_factory=list)
    temperature: float = 0.7


class WorkflowConfig(BaseModel):
    name: str
    description: str = ""
    agents: list[AgentConfig]
    max_iterations: int = 10


class AgentMessage(BaseModel):
    role: str
    content: str
    agent: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict)


class WorkflowRun(BaseModel):
    id: str = ""
    workflow_name: str
    status: str = "pending"
    messages: list[AgentMessage] = Field(default_factory=list)
    result: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    duration_ms: int = 0
    token_usage: dict = Field(default_factory=dict)


# --- RAG Schemas ---


class DocumentUpload(BaseModel):
    filename: str
    content: str
    metadata: dict = Field(default_factory=dict)


class DocumentChunk(BaseModel):
    id: str
    content: str
    metadata: dict = Field(default_factory=dict)
    embedding: list[float] = Field(default_factory=list)
    similarity: float = 0.0


class RAGQuery(BaseModel):
    query: str
    top_k: int = 5
    filters: dict = Field(default_factory=dict)


class RAGResponse(BaseModel):
    answer: str
    sources: list[DocumentChunk]
    model: str
    tokens_used: int = 0


# --- Eval Schemas ---


class EvalRequest(BaseModel):
    prompt: str
    models: list[LLMProvider] = Field(default_factory=lambda: [LLMProvider.CLAUDE])
    temperature: float = 0.7
    max_tokens: int = 1024
    num_runs: int = 1


class EvalMetrics(BaseModel):
    relevance: float = 0.0
    coherence: float = 0.0
    faithfulness: float = 0.0
    latency_ms: int = 0
    tokens_used: int = 0
    cost_usd: float = 0.0


class EvalResult(BaseModel):
    model: LLMProvider
    response: str
    metrics: EvalMetrics
    guardrail_flags: list[str] = Field(default_factory=list)


class EvalComparison(BaseModel):
    prompt: str
    results: list[EvalResult]
    winner: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)


# --- Guardrail Schemas ---


class GuardrailCheck(BaseModel):
    type: GuardrailType
    passed: bool
    score: float = 0.0
    details: str = ""


class GuardrailResult(BaseModel):
    input_text: str
    checks: list[GuardrailCheck]
    blocked: bool = False
    sanitized_text: str = ""
