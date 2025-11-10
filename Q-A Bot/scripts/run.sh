#!/usr/bin/env bash
set -euo pipefail
python src/ingest.py --data_dir data --persist_dir db
chainlit run src/app.py -w
