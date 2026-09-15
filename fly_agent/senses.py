from __future__ import annotations

import re
from dataclasses import dataclass

from .types import SenseSignal


# Placeholder encoder. Replace this with an embedding/image/environment encoder
# before treating the system as more than a scaffold.
SENSES: dict[str, tuple[list[str], str]] = {
    "threat": (["LC4", "LPLC2"], "a huge shape looming at it (looming detectors)"),
    "taste": (["claw_tpGRN", "dorsal_tpGRN", "BM_Taste"], "something tasty on its mouthparts (taste neurons)"),
    "mate": (["LC10a"], "another fly moving nearby (moving-target detectors)"),
    "wind": (
        ["JO-CL", "JO-CM", "JO-CA2", "JO-EV1", "JO-EV2", "JO-EV3", "JO-EV5", "JO-EV6", "JO-ED1",
         "JO-ED2_a", "JO-ED2_b", "JO-ED2_c"],
        "wind on its antennae (Johnston's organ)",
    ),
    "touch": (["BM_InOm"], "something brushing its eyes (eye bristles)"),
    "smell": (["ORN_DA1"], "the smell of another male (cVA pheromone receptors)"),
    "nothing": ([], "nothing in particular"),
}

KEYWORDS: dict[str, str] = {
    "threat": r"swat|slap|kill|\bhit\b|attack|danger|scary|monster|boss|deadline|\bbugs?\b|crash|error|fail|angry|shout|spider|bird|\bhands?\b|\brun\b|urgent|panic|police|tax",
    "taste": r"pizza|food|eat|hungry|sugar|sweet|cake|fruit|banana|apple|wine|beer|coffee|juice|lunch|dinner|snack|honey|candy|trash|garbage|rotten|burger",
    "mate": r"\bhi\b|hello|hey|cute|love|date|kiss|crush|friend|party|meet|dance|flirt|beautiful|handsome|single|tinder|gm\b",
    "wind": r"wind|fan|blow|breeze|air|storm|cold|ac\b|window|fly away|fast",
    "touch": r"touch|poke|tickle|pet|hug|scratch|brush|rub|itch|face|eye",
    "smell": r"smell|perfume|cologne|stink|scent|odou?r|fart|sweat|deodorant",
}


@dataclass(frozen=True)
class LexiconSenseEncoder:
    """Small, inspectable text-to-sense encoder.

    It is deliberately not semantic: the lexicon is a bootstrap. The design goal
    is to keep the hand-written part isolated so it can be replaced without
    touching the brain loop.
    """

    case_sensitive: bool = False

    def encode(self, text: str) -> SenseSignal:
        source = text if self.case_sensitive else text.lower()
        scores = {name: len(re.findall(pattern, source)) for name, pattern in KEYWORDS.items()}
        best = max(scores, key=scores.get)
        sense = best if scores[best] > 0 else "nothing"
        cells, felt = SENSES[sense]
        return SenseSignal(
            sense=sense,
            stimulated=tuple(cells),
            felt=felt,
            score=float(scores[best]),
            notes={"scores": scores},
        )
