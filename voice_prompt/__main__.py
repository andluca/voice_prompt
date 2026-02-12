"""Allow running as: python -m voice_prompt"""

import os
import sys

# When running under pythonw.exe, stdout/stderr don't exist.
# Redirect to devnull so rich/logging don't crash.
if sys.executable.endswith("pythonw.exe") or sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
    sys.stderr = open(os.devnull, "w")

from voice_prompt.main import cli

cli()
