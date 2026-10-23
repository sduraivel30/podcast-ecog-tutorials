#!/bin/bash
#SBATCH --job-name=podcast_setup
#SBATCH --partition=pi_evelina9,ou_bcs_normal,ou_bcs_low
#SBATCH --time=3:00:00
#SBATCH --mem=8GB
#SBATCH --cpus-per-task=2
#SBATCH --output=logs/setup_%j.out
# One-off setup on ORCD: python venv (miniforge python), requirements, and the full ds005574 download (public S3 bucket, ~14.4 GiB) next to the other lab data.
set -e
cd "${SLURM_SUBMIT_DIR:-$(dirname "$0")/..}"; mkdir -p logs   # under sbatch $0 is a spooled copy: submit from the repo directory
DATA=/orcd/data/evelina9/001/USERS/sdurai30/data/podcast_ecog
module load miniforge
[ -d .venv ] || python -m venv .venv
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q -r requirements.txt awscli
.venv/bin/pip install -q -e .
mkdir -p "$DATA" external
[ -d external/podcast-ecog-tutorials ] || git clone -q --depth 1 https://github.com/hassonlab/podcast-ecog-tutorials external/podcast-ecog-tutorials
[ -d external/podcast-ecog-paper ] || git clone -q --depth 1 https://github.com/hassonlab/podcast-ecog-paper external/podcast-ecog-paper
.venv/bin/aws s3 sync --no-sign-request s3://openneuro.org/ds005574 "$DATA" --only-show-errors
echo "export PODCAST_BIDS_ROOT=$DATA" > .env.server
echo "done $(date): $(du -sh $DATA | cut -f1) in $DATA"
