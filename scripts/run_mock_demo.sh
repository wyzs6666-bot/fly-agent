#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m fly_agent.cli --brain mock "the boss deadline is going to crash and fail"
python -m fly_agent.cli --brain mock --fragile "a huge hand is going to swat the fly"
python -m fly_agent.cli --brain mock --quiet "wind from the fan is strong"
