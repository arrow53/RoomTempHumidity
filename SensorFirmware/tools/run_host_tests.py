"""Run schema tests, then actual C core tests if an existing C compiler is available."""
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_schema.py", "-v"], cwd=ROOT, check=True)
compiler = os.environ.get("CC") or next((shutil.which(c) for c in ("clang", "gcc", "cc") if shutil.which(c)), None)
if not compiler:
    print("SKIP: C unit tests require an existing clang/gcc/cc compiler (or CC executable path).")
    print("INFO: target builds and hardware verification are separate from this host test runner.")
    sys.exit(0)
build = ROOT / "build-host"
build.mkdir(exist_ok=True)
exe = build / ("test_core.exe" if os.name == "nt" else "test_core")
subprocess.run([compiler, "-std=c11", "-Wall", "-Wextra", "-Werror", "-Iinclude", "src/reading.c", "src/boot_id.c", "src/sequence.c", "tests/test_core.c", "-o", str(exe)], cwd=ROOT, check=True)
output = subprocess.check_output([str(exe)], text=True, cwd=ROOT)
sys.path.insert(0, str(ROOT / "tools"))
from validate_payload import load_payload
load_payload(output)
(build / "actual-serialized-reading.json").write_text(output, encoding="utf-8")
print("PASS: C measurements/serialization/sequence tests and schema validation of actual C output.")
