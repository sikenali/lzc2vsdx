#!/usr/bin/env python3
"""用 PyInstaller 把 Flask 后端打成单文件可执行程序。

输出：electron/resources/backend/c2vsdx-backend(.exe)
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import PyInstaller.__main__

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
OUT = ROOT / "electron" / "resources" / "backend"
WORK = ROOT / "build" / "pyinstaller"

HIDDEN_IMPORTS = [
    "config",
    "generate",
    "parser",
    "jobs",
    "compact_layout",
    "render_image",
    "graphviz",
    "graphviz.backend",
    "graphviz.backend.execute",
    "flowchart.models",
    "flowchart.layout_engine",
    "flowchart.renderer",
    "sequence.models",
    "sequence.layout_engine",
    "sequence.renderer",
    "composition.models",
    "composition.layout_engine",
    "composition.renderer",
    "component.models",
    "component.layout_engine",
    "component.renderer",
    "architecture.models",
    "architecture.layout_engine",
    "architecture.renderer",
    "swimlane.models",
    "swimlane.layout_engine",
    "swimlane.renderer",
    "image2visio.image2visio",
]

if sys.platform == "win32":
    HIDDEN_IMPORTS += [
        "win32com",
        "win32com.client",
        "pythoncom",
        "pywintypes",
        "win32api",
        "win32con",
    ]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    # Windows 不跑 bundle_graphviz_linux.sh，这里保证 extraResources 的目录存在
    (ROOT / "electron" / "resources" / "graphviz-linux").mkdir(parents=True, exist_ok=True)

    args = [
        "--noconfirm",
        "--clean",
        "--onefile",
        "--name",
        "c2vsdx-backend",
        "--distpath",
        str(OUT),
        "--workpath",
        str(WORK),
        "--specpath",
        str(WORK),
        "--paths",
        str(BACKEND),
        "--add-data",
        f"{BACKEND / 'c2vsdx'}{os.pathsep}c2vsdx",
        "--collect-submodules",
        "flask",
    ]
    for name in HIDDEN_IMPORTS:
        args += ["--hidden-import", name]

    args.append(str(BACKEND / "app.py"))
    PyInstaller.__main__.run(args)
    print(f"backend binary written to {OUT}")


if __name__ == "__main__":
    main()
