from dataclasses import dataclass
from typing import Any

from anthropic import Anthropic


client = Anthropic()


@dataclass
class MemoryCandidate:
    should_store: bool
    content: str | None = None
    title: str | None = None
    memory_type: str | None = None
    scope: str | None = None
    repository: str | None = None
    importance: float | None = None
    retention_policy: str | None = None
    expires_at: str | None = None
    sensitivity: str | None = None
    requires_consent: bool = False
    reason: str | None = None


MEMORY_TOOL = {
    "name": "classify_memory",
    "description": """
Determine whether the conversation contains durable information worth storing.

Store:
- Preferences and recurring workflows
- Long-lived facts
- Architecture decisions
- Coding conventions
- Resolved debugging investigations
- Resumable task state
- Reusable documentation or implementation notes
- Summaries containing durable information

Do not store:
- One-off questions
- Casual conversation
- Temporary brainstorming
- Intermediate reasoning
- Current-session-only information
- Duplicate memories
- Sensitive information without explicit consent

Return one clear, self-contained memory rather than copying the conversation.
""",
    "input_schema": {
        "type": "object",
        "properties": {
            "should_store": {
                "type": "boolean"
            },
            "content": {
                "type": ["string", "null"]
            },
            "title": {
                "type": ["string", "null"]
            },
            "memory_type": {
                "type": ["string", "null"],
                "enum": [
                    "architecture",
                    "coding_convention",
                    "preference",
                    "recurring_workflow",
                    "long_lived_fact",
                    "debugging",
                    "task_state",
                    "documentation",
                    "implementation_note",
                    "conversation_summary",
                    None,
                ],
            },
            "scope": {
                "type": ["string", "null"],
                "enum": [
                    "personal",
                    "team",
                    None,
                ],
            },
            "repository": {
                "type": ["string", "null"]
            },
            "importance": {
                "type": ["number", "null"],
                "minimum": 0,
                "maximum": 1,
            },
            "retention_policy": {
                "type": ["string", "null"],
                "enum": [
                    "until_deleted",
                    "until_superseded",
                    "temporary",
                    None,
                ],
            },
            "expires_at": {
                "type": ["string", "null"],
                "description": (
                    "ISO-8601 timestamp for temporary memories. "
                    "Use null for non-temporary memories."
                ),
            },
            "sensitivity": {
                "type": ["string", "null"],
                "enum": [
                    "normal",
                    "sensitive",
                    None,
                ],
            },
            "requires_consent": {
                "type": "boolean"
            },
            "reason": {
                "type": ["string", "null"]
            },
        },
        "required": [
            "should_store",
            "content",
            "title",
            "memory_type",
            "scope",
            "repository",
            "importance",
            "retention_policy",
            "expires_at",
            "sensitivity",
            "requires_consent",
            "reason",
        ],
    },
}


def validate_candidate(data: dict[str, Any]) -> MemoryCandidate:
    """
    Validate Claude's proposed memory before Brain accepts it.
    """
    should_store = data.get("should_store", False)

    if not should_store:
        return MemoryCandidate(
            should_store=False,
            reason=data.get("reason"),
        )

    content = data.get("content")
    title = data.get("title")
    importance = data.get("importance")
    sensitivity = data.get("sensitivity") or "normal"
    requires_consent = data.get("requires_consent", False)
    retention_policy = data.get("retention_policy")
    expires_at = data.get("expires_at")

    if not isinstance(content, str) or not content.strip():
        raise ValueError("Stored memory must have content.")

    if not isinstance(title, str) or not title.strip():
        raise ValueError("Stored memory must have a title.")

    if not isinstance(importance, (int, float)):
        raise ValueError("Importance must be a number.")

    if not 0 <= importance <= 1:
        raise ValueError("Importance must be between 0 and 1.")

    if sensitivity == "sensitive" and not requires_consent:
        raise ValueError(
            "Sensitive memories must require explicit user consent."
        )

    if retention_policy == "temporary" and not expires_at:
        raise ValueError(
            "Temporary memories must include an expires_at timestamp."
        )

    if retention_policy != "temporary" and expires_at is not None:
        raise ValueError(
            "Only temporary memories should have expires_at."
        )

    return MemoryCandidate(
        should_store=True,
        content=content.strip(),
        title=title.strip(),
        memory_type=data.get("memory_type"),
        scope=data.get("scope"),
        repository=data.get("repository"),
        importance=float(importance),
        retention_policy=retention_policy,
        expires_at=expires_at,
        sensitivity=sensitivity,
        requires_consent=requires_consent,
        reason=data.get("reason"),
    )


def extract_memory(
    conversation: str,
    repository: str | None = None,
) -> MemoryCandidate:
    """
    Ask Claude whether the conversation contains a durable memory.
    """
    if not conversation.strip():
        return MemoryCandidate(
            should_store=False,
            reason="Conversation was empty.",
        )

    repository_context = repository or "unknown"

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        tools=[MEMORY_TOOL],
        tool_choice={
            "type": "tool",
            "name": "classify_memory",
        },
        messages=[
            {
                "role": "user",
                "content": (
                    f"Current repository: {repository_context}\n\n"
                    f"Conversation:\n{conversation}"
                ),
            }
        ],
    )

    for block in response.content:
        if (
            block.type == "tool_use"
            and block.name == "classify_memory"
        ):
            return validate_candidate(block.input)

    raise RuntimeError(
        "Claude did not return a memory classification."
    )
# design decision
#     Important design decision

# Retention should depend on memory type:

# Architecture/coding conventions: keep until superseded
# Preferences: keep until updated or removed
# Task state: short TTL
# Temporary investigation notes: expire after a set period
# Conversation summaries: retain only when they remain useful

# So we should add fields like:

# expires_at
# retention_policy
# sensitivity
# requires_consent