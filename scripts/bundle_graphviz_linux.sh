#!/usr/bin/env bash
# 把 Linux 系统的 Graphviz dot 及其私有库复制到 Electron 资源目录，
# 让 AppImage 在未安装 Graphviz 的机器上也能计算流程图/关系图布局。
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PREFIX="${GRAPHVIZ_ROOT:-/usr}"
OUT="$ROOT/electron/resources/graphviz-linux"
LIBDIR="$PREFIX/lib/x86_64-linux-gnu"

rm -rf "$OUT"
mkdir -p "$OUT/bin" "$OUT/lib/graphviz"

cp -L "$PREFIX/bin/dot" "$OUT/bin/dot"
chmod +x "$OUT/bin/dot"

for pattern in \
  "libgvc.so.6*" \
  "libcgraph.so.6*" \
  "libcdt.so.5*" \
  "libpathplan.so.4*" \
  "libxdot.so.4*" \
  "libgts-0.7.so.5*" \
  "libann.so.0*" \
  "libgvpr.so.2*" \
  "liblab_gamut.so.1*"; do
  for file in "$LIBDIR"/$pattern; do
    [ -e "$file" ] && cp -a "$file" "$OUT/lib/"
  done
done

cp -a "$LIBDIR/graphviz/." "$OUT/lib/graphviz/"

# 生成/确认插件配置，确保 dot 在包内能找到插件
LD_LIBRARY_PATH="$OUT/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" \
GVBINDIR="$OUT/lib/graphviz" \
"$OUT/bin/dot" -c >/dev/null 2>&1 || true

echo "bundled graphviz -> $OUT"
LD_LIBRARY_PATH="$OUT/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" \
GVBINDIR="$OUT/lib/graphviz" \
"$OUT/bin/dot" -V || true
