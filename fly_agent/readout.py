from __future__ import annotations

from .types import BrainObservation


def choose_actions(obs: BrainObservation) -> tuple[list[str], dict[str, str]]:
    """Turn extra spikes in behaviour groups into abstract actions.

    Thresholds are conservative defaults, not biological facts. Change them only
    with controls: rest baseline, scrambled wiring, and no-stimulus baseline.
    """

    extra = obs.extra_spikes
    rest = obs.rest
    reasons: dict[str, str] = {}

    def add(action: str, reason: str) -> None:
        if action not in reasons:
            reasons[action] = reason

    if extra.get("escape", 0.0) >= 3.0:
        add("jumped", f"escape +{extra['escape']:.1f} spikes")

    wing_threshold = max(15.0, 0.25 * rest.get("wings", 0.0))
    if extra.get("wings", 0.0) >= wing_threshold:
        add("buzzed its wings", f"wings +{extra['wings']:.1f} >= {wing_threshold:.1f}")

    if extra.get("groom", 0.0) >= max(10.0, 0.25 * rest.get("groom", 0.0)):
        add("groomed", f"groom +{extra['groom']:.1f}")

    turn_extra = extra.get("steer_left", 0.0) + extra.get("steer_right", 0.0)
    if turn_extra >= 3.0:
        side = extra.get("steer_left", 0.0) - extra.get("steer_right", 0.0)
        if side >= 1.0:
            add("turned left", f"steer asymmetry {side:.1f}")
        elif side <= -1.0:
            add("turned right", f"steer asymmetry {side:.1f}")
        else:
            add("turned", f"steer total +{turn_extra:.1f}")

    if extra.get("walk", 0.0) >= 3.0:
        add("walked forward", f"walk +{extra['walk']:.1f}")
    if extra.get("back", 0.0) >= 3.0:
        add("backed up", f"back +{extra['back']:.1f}")

    return list(reasons), reasons
