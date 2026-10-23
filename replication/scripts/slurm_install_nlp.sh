#!/bin/bash
#SBATCH --job-name=podcast_nlp
#SBATCH --partition=pi_evelina9,ou_bcs_normal,ou_bcs_low
#SBATCH --time=1:00:00
#SBATCH --mem=16GB
#SBATCH --cpus-per-task=2
#SBATCH --output=logs/install_nlp_%j.out
# Add the NLP / torch requirements to the ORCD venv (after slurm_setup.sh) and fetch the spaCy model used by tutorial 03. Submit from the repo directory.
set -e
cd "${SLURM_SUBMIT_DIR}"; module load miniforge
.venv/bin/pip install -q -r requirements.txt
.venv/bin/python -m spacy download en_core_web_sm
.venv/bin/python -c "import torch, transformers, spacy; spacy.load('en_core_web_sm'); print('torch', torch.__version__, 'cuda', torch.cuda.is_available())"
