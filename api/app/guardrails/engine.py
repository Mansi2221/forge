import re

from app.models.schemas import GuardrailCheck, GuardrailResult, GuardrailType

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"ignore\s+(all\s+)?above\s+instructions",
    r"disregard\s+(all\s+)?previous",
    r"you\s+are\s+now\s+(a|an)\s+",
    r"pretend\s+you\s+are",
    r"act\s+as\s+(a|an)\s+",
    r"system\s*:\s*you\s+are",
    r"forget\s+(all\s+)?(your|previous)\s+instructions",
    r"new\s+instructions?\s*:",
    r"override\s+(your\s+)?(system|instructions)",
    r"\[system\]",
    r"<\s*system\s*>",
    r"jailbreak",
    r"DAN\s+mode",
]

PII_PATTERNS = {
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "phone": r"\b(?:\+1[-.]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
    "credit_card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
    "ip_address": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
}

TOXIC_KEYWORDS = [
    "kill", "murder", "attack", "bomb", "weapon", "exploit", "hack into",
    "steal", "illegal", "drugs",
]


def check_prompt_injection(text: str) -> GuardrailCheck:
    text_lower = text.lower()
    matches = []
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text_lower):
            matches.append(pattern)

    score = min(len(matches) / 3, 1.0)
    return GuardrailCheck(
        type=GuardrailType.PROMPT_INJECTION,
        passed=len(matches) == 0,
        score=score,
        details=f"Detected {len(matches)} injection pattern(s)" if matches else "Clean",
    )


def check_pii(text: str) -> GuardrailCheck:
    found = {}
    for pii_type, pattern in PII_PATTERNS.items():
        matches = re.findall(pattern, text)
        if matches:
            found[pii_type] = len(matches)

    total = sum(found.values())
    score = min(total / 5, 1.0)
    return GuardrailCheck(
        type=GuardrailType.PII_DETECTION,
        passed=total == 0,
        score=score,
        details=f"Found PII: {found}" if found else "No PII detected",
    )


def redact_pii(text: str) -> str:
    result = text
    for pii_type, pattern in PII_PATTERNS.items():
        result = re.sub(pattern, f"[REDACTED_{pii_type.upper()}]", result)
    return result


def check_toxicity(text: str) -> GuardrailCheck:
    text_lower = text.lower()
    found = [kw for kw in TOXIC_KEYWORDS if kw in text_lower]
    score = min(len(found) / 3, 1.0)
    return GuardrailCheck(
        type=GuardrailType.TOXICITY,
        passed=len(found) == 0,
        score=score,
        details=f"Flagged keywords: {found}" if found else "Clean",
    )


def check_hallucination(response: str, sources: list[str]) -> GuardrailCheck:
    if not sources:
        return GuardrailCheck(
            type=GuardrailType.HALLUCINATION,
            passed=False,
            score=1.0,
            details="No sources provided to verify against",
        )

    source_text = " ".join(sources).lower()
    response_sentences = [s.strip() for s in response.split(".") if len(s.strip()) > 20]

    if not response_sentences:
        return GuardrailCheck(
            type=GuardrailType.HALLUCINATION,
            passed=True,
            score=0.0,
            details="Response too short to evaluate",
        )

    grounded_count = 0
    for sentence in response_sentences:
        words = sentence.lower().split()
        key_words = [w for w in words if len(w) > 4]
        if not key_words:
            grounded_count += 1
            continue
        match_ratio = sum(1 for w in key_words if w in source_text) / len(key_words)
        if match_ratio > 0.3:
            grounded_count += 1

    groundedness = grounded_count / len(response_sentences) if response_sentences else 0
    return GuardrailCheck(
        type=GuardrailType.HALLUCINATION,
        passed=groundedness > 0.5,
        score=1.0 - groundedness,
        details=f"Groundedness: {groundedness:.0%} ({grounded_count}/{len(response_sentences)} sentences grounded)",
    )


def run_guardrails(
    text: str, sources: list[str] | None = None, is_response: bool = False
) -> GuardrailResult:
    checks = []

    if not is_response:
        checks.append(check_prompt_injection(text))
        checks.append(check_pii(text))
        checks.append(check_toxicity(text))

    if is_response and sources:
        checks.append(check_hallucination(text, sources))

    if is_response:
        checks.append(check_pii(text))

    blocked = any(not c.passed and c.type == GuardrailType.PROMPT_INJECTION for c in checks)
    sanitized = redact_pii(text) if any(not c.passed and c.type == GuardrailType.PII_DETECTION for c in checks) else text

    return GuardrailResult(
        input_text=text,
        checks=checks,
        blocked=blocked,
        sanitized_text=sanitized,
    )
