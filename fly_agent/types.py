from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SenseSignal:
    """What the agent decides to let the fly brain sense.

    This is intentionally explicit: in real mode, `stimulated` must contain
    MaleCNS cell types or superclasses that `FlyBrain.cells(...)` understands.
    """

    sense: str
    stimulated: tuple[str, ...]
    felt: str
    score: float = 1.0
    notes: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BrainObservation:
    """One stimulus-vs-rest comparison from the frozen connectome."""

    sense: str
    felt: str
    stimulated: tuple[str, ...]
    rest: dict[str, float]
    felt_rates: dict[str, float]
    extra_spikes: dict[str, float]
    top_descending_neurons: list[dict[str, float]]
    wing_spikes_per_s: float
    n_neurons: int | None
    note: str


@dataclass(frozen=True)
class AgentResult:
    text_input: str
    mode: str
    sense: str
    felt: str
    actions: list[str]
    evidence: dict[str, Any]
    brain_log: str
    policy_note: str = ""
