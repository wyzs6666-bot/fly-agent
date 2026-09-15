from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .agent import create_agent, result_to_dict


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a small agent with a frozen fruit-fly connectome reflex core.")
    parser.add_argument("message", nargs="*", help="text to encode into a fly sense")
    parser.add_argument("--brain", choices=["auto", "real", "mock"], default="auto", help="real requires `pip install flybrain`")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--fragile", action="store_true", help="replace escape jump with recoil")
    parser.add_argument("--quiet", action="store_true", help="suppress wing buzzing")
    args = parser.parse_args(argv)

    text = " ".join(args.message).strip() or "nothing happened"
    context: dict[str, Any] = {}
    if args.fragile:
        context["fragile"] = True
    if args.quiet:
        context["quiet"] = True

    try:
        agent = create_agent(mode=args.brain, seed=args.seed)
        result = agent.handle(text, context=context, seed=args.seed)
    except Exception as exc:
        print(json.dumps({"error": str(exc), "hint": "try `fly-agent --brain mock ...` or `pip install flybrain`"}, indent=2))
        return 2

    print(json.dumps(result_to_dict(result), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
