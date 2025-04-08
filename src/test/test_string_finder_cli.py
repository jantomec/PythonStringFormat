import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

SRC = """# This is a simple script that prints a greeting message.
f"Hello, {__name__}!"

a = 1
b = 2
"Sum of {} and {} is {}".format(a, b, a+b)
"""

process = subprocess.Popen(
    ["python", "src/string_finder.py", "3", "0"],
    stdin=subprocess.PIPE
)
process.stdin.write(SRC.encode('utf-8'))
process.stdin.close()

print("Return code:", process.wait())
