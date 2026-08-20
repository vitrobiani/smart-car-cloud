from dataclasses import dataclass
from typing import Any, Callable

from app.orchestrator.context import ContextSnapshot


@dataclass
class RuleResult:
    action: str  # e.g. "coach", "warn", "chatbot", "none"
    priority: int
    message: str | None = None


Rule = Callable[[ContextSnapshot, dict[str, Any]], RuleResult | None]

RULES: list[Rule] = []


def register_rule(rule: Rule) -> Rule:
    RULES.append(rule)
    return rule
