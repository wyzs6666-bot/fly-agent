from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .brain_core import BrainCore, FlyBrainCore, MockBrainCore
from .readout import choose_actions
from .safety import SafetyPolicy
from .senses import LexiconSenseEncoder
from .types import AgentResult


class FlyAgent:
    """Language-facing agent with a frozen fruit-fly connectome as its reflex core."""

    def __init__(self, core: BrainCore, encoder: LexiconSenseEncoder | None = None, policy: SafetyPolicy | None = None):
        self.core = core
        self.encoder = encoder or LexiconSenseEncoder()
        self.policy = policy or SafetyPolicy()

    def handle(self, text: str, context: dict[str, Any] | None = None, seed: int = 7) -> AgentResult:
        signal = self.encoder.encode(text)
        observation = self.core.observe(signal, seed=seed)
        proposed, reasons = choose_actions(observation)
        actions, policy_note = self.policy.filter(proposed, context)
        top = observation.top_descending_neurons[:2]
        top_txt = ", ".join(f"{item['type']}(+{item['extra_spikes']:.1f})" for item in top) or "none"
        brain_log = f"felt: {observation.felt} · top neurons: {top_txt} · did: {', '.join(actions)}"
        evidence = {
            "sense_scores": signal.notes.get("scores", {}),
            "stimulated": list(signal.stimulated),
            "extra_spikes": observation.extra_spikes,
            "rest": observation.rest,
            "top_descending_neurons": observation.top_descending_neurons,
            "reasons": reasons,
            "brain_note": observation.note,
            "n_neurons": observation.n_neurons,
        }
        return AgentResult(
            text_input=text,
            mode=self.core.mode,
            sense=signal.sense,
            felt=observation.felt,
            actions=actions,
            evidence=evidence,
            brain_log=brain_log,
            policy_note=policy_note,
        )


def create_agent(mode: str = "auto", seed: int = 7, **brain_kwargs: Any) -> FlyAgent:
    if mode not in {"auto", "real", "mock"}:
        raise ValueError("mode must be one of: auto, real, mock")
    fallback_note = ""
    if mode in {"auto", "real"}:
        try:
            return FlyAgent(FlyBrainCore(seed=seed, **brain_kwargs))
        except Exception as exc:  # auto falls back; real surfaces the error
            if mode == "real":
                raise
            fallback_note = f"real brain unavailable, using mock: {exc}"
    return FlyAgent(MockBrainCore(seed=seed, note=fallback_note or "mock brain: no neurons simulated"))


def result_to_dict(result: AgentResult) -> dict[str, Any]:
    return asdict(result)
