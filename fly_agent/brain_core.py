from __future__ import annotations

import random
from typing import Protocol

import numpy as np

from .types import BrainObservation, SenseSignal

WARM_STEPS = 25
STIM_STEPS = 50
DT = 0.020
AMOUNT = 0.8
RUNS = 3

# From alextitonis/fly.ai (MIT); see NOTICE.md.
WING_MN = [
    "DLMn a, b", "DLMn c-f", "DVMn 1a-c", "DVMn 2a, b", "DVMn 3a, b", "MNwm35", "MNwm36",
    "b1 MN", "b2 MN", "b3 MN", "hg1 MN", "hg2 MN", "hg3 MN", "hg4 MN", "i1 MN", "i2 MN",
    "iii1 MN", "iii3 MN", "ps1 MN", "tp1 MN", "tp2 MN", "tpn MN",
]

BEHAVIOUR_GROUPS = ("escape", "steer_left", "steer_right", "walk", "back", "groom", "wings")


class BrainCore(Protocol):
    mode: str

    def observe(self, signal: SenseSignal, seed: int = 7, runs: int = RUNS) -> BrainObservation:
        ...


class FlyBrainCore:
    """Adapter around the optional `flybrain` package.

    The connectome is frozen: this class only stimulates sensory/feature neurons,
    steps the spiking network, and compares stimulus vs rest.
    """

    mode = "real"

    def __init__(self, seed: int = 7, device: str | None = None, data: str | None = None, sensory_input: bool = False):
        try:
            from flybrain import FlyBrain
        except ImportError as exc:  # pragma: no cover - depends on optional env
            raise RuntimeError("real brain mode needs `pip install flybrain`") from exc
        self.brain = FlyBrain(batch=1, dt=DT, device=device, data=data, sensory_input=sensory_input)
        self.seed = seed
        self.n = int(self.brain.n)
        self.groups = self._behaviour_groups()
        self.descending = self.brain.cells(["descending_neuron"])
        self.descending_col = np.full(self.n, -1, dtype=np.int64)
        self.descending_col[self.descending] = np.arange(len(self.descending))

    def _mask(self, ids: np.ndarray) -> np.ndarray:
        mask = np.zeros(self.n, dtype=bool)
        mask[np.asarray(ids, dtype=np.int64)] = True
        return mask

    def _behaviour_groups(self) -> dict[str, np.ndarray]:
        b = self.brain
        types = np.unique(b.cell_type.astype(str))
        concat = lambda *xs: np.concatenate([np.asarray(x, dtype=np.int64) for x in xs])
        return {
            "escape": self._mask(concat(b.groups["escape_L"], b.groups["escape_R"])),
            "steer_left": self._mask(b.groups["steer_L"]),
            "steer_right": self._mask(b.groups["steer_R"]),
            "walk": self._mask(concat(b.groups["forward_L"], b.groups["forward_R"])),
            "back": self._mask(concat(b.groups["backward_L"], b.groups["backward_R"])),
            "groom": self._mask(b.cells([t for t in types if t.startswith("DNg12")])),
            "wings": self._mask(b.cells(WING_MN)),
        }

    def _episode(self, stim_cells: np.ndarray, seed: int) -> tuple[dict[str, float], np.ndarray]:
        b = self.brain
        b.reset(seed)
        counts = {name: 0.0 for name in BEHAVIOUR_GROUPS}
        dn_counts = np.zeros(len(self.descending), dtype=np.float64)
        for step in range(WARM_STEPS + STIM_STEPS):
            inject = [(stim_cells, AMOUNT)] if step >= WARM_STEPS and len(stim_cells) else []
            fired = b.step(inject=inject)
            if step < WARM_STEPS:
                continue
            fired = np.asarray(fired, dtype=np.int64)
            for name, mask in self.groups.items():
                counts[name] += float(mask[fired].sum())
            col = self.descending_col[fired]
            np.add.at(dn_counts, col[col >= 0], 1)
        return counts, dn_counts

    def observe(self, signal: SenseSignal, seed: int = 7, runs: int = RUNS) -> BrainObservation:
        stim = np.array(signal.stimulated, dtype=object)
        stim_cells = self.brain.cells(list(stim)) if len(stim) else np.array([], dtype=np.int64)
        rest = {name: 0.0 for name in BEHAVIOUR_GROUPS}
        felt = {name: 0.0 for name in BEHAVIOUR_GROUPS}
        rest_dn = np.zeros(len(self.descending), dtype=np.float64)
        felt_dn = np.zeros(len(self.descending), dtype=np.float64)
        for r in range(runs):
            c0, d0 = self._episode(np.array([], dtype=np.int64), seed + r)
            c1, d1 = self._episode(stim_cells, seed + r)
            for name in BEHAVIOUR_GROUPS:
                rest[name] += c0[name] / runs
                felt[name] += c1[name] / runs
            rest_dn += d0 / runs
            felt_dn += d1 / runs
        extra = {name: felt[name] - rest[name] for name in BEHAVIOUR_GROUPS}
        dn_types = self.brain.cell_type[self.descending].astype(str)
        by_type: dict[str, float] = {}
        for cell_type, value in zip(dn_types, felt_dn - rest_dn):
            by_type[cell_type] = by_type.get(cell_type, 0.0) + float(value)
        top = [
            {"type": t, "extra_spikes": round(v, 3)}
            for t, v in sorted(by_type.items(), key=lambda kv: -kv[1])[:5]
            if v > 0.5
        ]
        return BrainObservation(
            sense=signal.sense,
            felt=signal.felt,
            stimulated=signal.stimulated,
            rest={k: round(v, 3) for k, v in rest.items()},
            felt_rates={k: round(v, 3) for k, v in felt.items()},
            extra_spikes={k: round(v, 3) for k, v in extra.items()},
            top_descending_neurons=top,
            wing_spikes_per_s=round(felt["wings"] / (STIM_STEPS * DT), 3),
            n_neurons=self.n,
            note="stimulus vs rest; frozen connectome; readouts are abstract actions, not proof of intent",
        )


class MockBrainCore:
    """Deterministic stand-in for interface tests and CI.

    It does not simulate neurons. It only makes the agent runnable before the
    optional flybrain package and ~260 MB connectome files are available.
    """

    mode = "mock"

    def __init__(self, seed: int = 7, note: str = "mock brain: no neurons simulated"):
        self.seed = seed
        self.note = note
        self.n = None

    def observe(self, signal: SenseSignal, seed: int = 7, runs: int = RUNS) -> BrainObservation:
        rng = random.Random(seed)
        rest = {
            "escape": 1.0,
            "steer_left": 1.2,
            "steer_right": 1.0,
            "walk": 1.5,
            "back": 0.8,
            "groom": 2.0,
            "wings": 4.0,
        }
        extra = {"escape": 0.0, "steer_left": 0.0, "steer_right": 0.0, "walk": 0.0, "back": 0.0, "groom": 0.0, "wings": 0.0}
        top: list[dict[str, float]] = []

        def jitter(scale: float = 1.0) -> float:
            return round(rng.uniform(-0.5, 0.5) * scale, 3)

        if signal.sense == "threat":
            extra.update({"escape": 18.0 + jitter(), "steer_left": 4.0 + jitter(), "wings": 3.0 + jitter()})
            top = [{"type": "DNp01", "extra_spikes": round(extra["escape"], 3)}]
        elif signal.sense == "wind":
            extra.update({"wings": 22.0 + jitter(), "escape": 4.0 + jitter()})
            top = [{"type": "DVMn", "extra_spikes": round(extra["wings"], 3)}]
        elif signal.sense == "touch":
            extra.update({"groom": 12.0 + jitter()})
            top = [{"type": "DNg12", "extra_spikes": round(extra["groom"], 3)}]
        elif signal.sense == "mate":
            extra.update({"steer_left": 4.5 + jitter()})
            top = [{"type": "DNa02", "extra_spikes": round(extra["steer_left"], 3)}]
        elif signal.sense == "smell":
            extra.update({"back": 4.0 + jitter()})
            top = [{"type": "MDN", "extra_spikes": round(extra["back"], 3)}]

        felt = {k: rest[k] + extra[k] for k in rest}
        return BrainObservation(
            sense=signal.sense,
            felt=signal.felt,
            stimulated=signal.stimulated,
            rest=rest,
            felt_rates={k: round(v, 3) for k, v in felt.items()},
            extra_spikes={k: round(v, 3) for k, v in extra.items()},
            top_descending_neurons=top,
            wing_spikes_per_s=round(felt["wings"] / (STIM_STEPS * DT), 3),
            n_neurons=self.n,
            note=self.note,
        )
