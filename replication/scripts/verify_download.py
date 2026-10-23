"""Compare a local copy of ds005574 with the public OpenNeuro bucket (file names and sizes): .venv/bin/python scripts/verify_download.py [root]   (needs the AWS CLI on PATH)."""
import subprocess, sys
from pathlib import Path
from podcast_ecog import bids_root
root = Path(sys.argv[1]) if len(sys.argv) > 1 else bids_root(); out = subprocess.run(["aws", "s3", "ls", "--no-sign-request", "--recursive", "s3://openneuro.org/ds005574/"], capture_output=True, text=True, check=True).stdout
remote = {l.split(None, 3)[3].replace("ds005574/", "", 1): int(l.split()[2]) for l in out.splitlines() if l.strip()}
missing = [k for k in remote if not (root / k).exists()]; bad = [k for k, s in remote.items() if (root / k).exists() and (root / k).stat().st_size != s]
print(f"{len(remote)} remote files, {len(missing)} missing, {len(bad)} with a different size")
for k in missing[:20]: print("  missing:", k)
for k in bad[:20]: print("  size mismatch:", k)
sys.exit(1 if missing or bad else 0)
