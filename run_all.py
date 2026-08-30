#!/usr/bin/env python3
"""Run the whole replication pipeline in order.

    python run_all.py            # everything
    python run_all.py --theory   # only the parts that need no data

Steps 1-4 and 6 require the EVS microdata (see data/README.md).
Step 5 (the theoretical figures) needs nothing but the code.
"""
import subprocess, sys
from pathlib import Path

CODE = Path(__file__).resolve().parent / "code"
NEEDS_DATA = ["01_prepare_data.py", "02_descriptives.py",
              "03_ordered_logit.py", "04_marginal_effects.py"]
NO_DATA = ["05_figures_theory.py"]
NEEDS_DATA_TAIL = ["06_figures_empirical.py"]

def run(script):
    print(f"\n===== {script} " + "=" * (60 - len(script)))
    r = subprocess.run([sys.executable, str(CODE / script)], cwd=CODE)
    if r.returncode:
        sys.exit(f"{script} failed with exit code {r.returncode}")

if __name__ == "__main__":
    theory_only = "--theory" in sys.argv
    scripts = NO_DATA if theory_only else NEEDS_DATA + NO_DATA + NEEDS_DATA_TAIL
    for s in scripts:
        run(s)
    print("\nDone.")
