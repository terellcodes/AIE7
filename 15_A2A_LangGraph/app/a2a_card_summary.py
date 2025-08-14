from __future__ import annotations

from typing import List

from a2a.types import AgentCard


def _format_capabilities(card: AgentCard) -> List[str]:
    caps = []
    try:
        cap = card.capabilities
        # Common capability flags; ignore if missing
        if getattr(cap, "streaming", None):
            caps.append("streaming")
        if getattr(cap, "push_notifications", None) or getattr(cap, "pushNotifications", None):
            caps.append("pushNotifications")
    except Exception:
        pass
    return caps


def _format_skills(card: AgentCard, limit: int = 5) -> List[str]:
    try:
        names = [s.name for s in (card.skills or []) if getattr(s, "name", None)]
        return names[:limit]
    except Exception:
        return []


def summarize_agent_card(card: AgentCard) -> str:
    """
    Produce a concise, human-readable one-liner summarizing name, version,
    capabilities, and top skills from an AgentCard.
    """
    name = getattr(card, "name", "Unknown Agent")
    version = getattr(card, "version", "")
    caps = _format_capabilities(card)
    skills = _format_skills(card)

    parts: List[str] = [f"Delegates queries to '{name}'"]
    if version:
        parts[-1] += f" v{version}"
    if caps:
        parts.append("Capabilities: " + ", ".join(caps))
    if skills:
        parts.append("Skills: " + ", ".join(skills))

    return ". ".join(parts) + "."


