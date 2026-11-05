import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

# 开发机上的 Graphviz（Linux 解包的 dot）；Windows 下原项目会用 graphviz-bin。
GV = Path("/tmp/opencode/gvbin")
if GV.exists():
    os.environ["PATH"] = f"{GV}:{os.environ.get('PATH', '')}"
    os.environ.setdefault("LD_LIBRARY_PATH", "/tmp/opencode/gv/usr/lib/x86_64-linux-gnu")

os.environ.setdefault("OPENVS_PROGRESS_DELAY", "0")
