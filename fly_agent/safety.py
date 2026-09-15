from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SafetyPolicy:
    """Whitelist and context guards for abstract actions.

    The fly brain proposes low-level behaviours; the agent decides whether they
    are executable. Keep this layer independent from the brain so a spiking
    surprise cannot directly become a side effect.
    """

    allowed_actions: frozenset[str] = frozenset(
        {
            "noop",
            "jumped",
            "recoil",
            "buzzed its wings",
            "groomed",
            "turned",
            "turned left",
            "turned right",
            "walked forward",
            "backed up",
        }
    )
    blocked_replacements: dict[str, str] = field(default_factory=lambda: {"jumped": "recoil"})

    def filter(self, actions: list[str], context: dict[str, Any] | None = None) -> tuple[list[str], str]:
        context = context or {}
        out: list[str] = []
        notes: list[str] = []
        for action in actions:
            if action not in self.allowed_actions:
                notes.append(f"blocked unlisted action: {action}")
                continue
            if context.get("fragile") and action in self.blocked_replacements:
                replacement = self.blocked_replacements[action]
                out.append(replacement)
                notes.append(f"context=fragile: {action} -> {replacement}")
                continue
            if context.get("quiet") and action == "buzzed its wings":
                notes.append("context=quiet: removed buzzed its wings")
                continue
            out.append(action)
        if not out:
            out = ["noop"]
        # de-duplicate while preserving order
        seen: set[str] = set()
        out = [a for a in out if not (a in seen or seen.add(a))]
        return out, "; ".join(notes)
