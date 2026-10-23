#!/bin/bash
# Download the whole "Podcast" ECoG dataset (OpenNeuro ds005574, ~14.4 GiB, CC BY) into data/ds005574 .
# Needs the AWS CLI (no credentials: public bucket). Re-running only fetches missing/changed files.
set -e
cd "$(dirname "$0")/.."
mkdir -p data external
aws s3 sync --no-sign-request s3://openneuro.org/ds005574 data/ds005574 --only-show-errors
echo "done: $(du -sh data/ds005574 | cut -f1) in data/ds005574"
