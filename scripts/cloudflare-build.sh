#!/usr/bin/env bash
set -euo pipefail
export PIP_DISABLE_PIP_VERSION_CHECK=1
python3 -m pip install -r requirements-build.txt
python3 scripts/build_cloudflare.py
