"""
Usage: python bump_version.py [major|minor|patch]

  major — 大規模な変更（アルゴリズム刷新・機能追加など）
  minor — 中規模な変更（UI追加・新パラメータ・新ねじ種類など）
  patch — 小規模な変更（バグ修正・表示調整・コメント変更など）
"""
import sys, re, pathlib

FILE = pathlib.Path(__file__).parent / "thread_cutting.py"
PAT  = re.compile(r'(_VERSION\s*=\s*["\'])(\d+)\.(\d+)\.(\d+)(["\'])')

src = FILE.read_text(encoding="utf-8")
m   = PAT.search(src)
if not m:
    print("ERROR: _VERSION not found in thread_cutting.py", file=sys.stderr)
    sys.exit(1)

major, minor, patch = int(m.group(2)), int(m.group(3)), int(m.group(4))
bump = (sys.argv[1] if len(sys.argv) > 1 else "patch").lower()

if bump == "major":
    major += 1; minor = 0; patch = 0
elif bump == "minor":
    minor += 1; patch = 0
elif bump == "patch":
    patch += 1
else:
    print(f"ERROR: unknown bump type '{bump}'. Use major / minor / patch.", file=sys.stderr)
    sys.exit(1)

new_ver = f"{major}.{minor}.{patch}"
FILE.write_text(PAT.sub(lambda mo: f"{mo.group(1)}{new_ver}{mo.group(5)}", src), encoding="utf-8")
print(new_ver)
