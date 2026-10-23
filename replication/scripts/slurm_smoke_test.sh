#!/bin/bash
#SBATCH --job-name=podcast_smoke
#SBATCH --partition=pi_evelina9,ou_bcs_normal,ou_bcs_low
#SBATCH --time=1:00:00
#SBATCH --mem=32GB
#SBATCH --cpus-per-task=8
#SBATCH --output=logs/smoke_%j.out
# Tests + tutorial-04 encoding for one subject on ORCD (after slurm_setup.sh). Usage: sbatch scripts/slurm_smoke_test.sh [subject]
set -e
cd "${SLURM_SUBMIT_DIR:-$(dirname "$0")/..}"; source .env.server
.venv/bin/python -m pytest -q tests
.venv/bin/python scripts/smoke_test.py --subject "${1:-03}" --n-channels 40
