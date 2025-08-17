# scripts/audit_font_coverage.py
# Miohalo · 字体覆盖侦察器（专治“问号顶帽子”和小方块）
# 运行：
#   python scripts/audit_font_coverage.py
# 产物：
#   data/out/font_coverage_report.txt
#   data/out/missing_glyphs.csv
#   data/out/missing_combining_marks.csv

import os, sys, json, csv, pathlib, unicodedata
from collections import Counter, defaultdict

# 用 matplotlib 的 FreeType 接口读 TTF 覆盖
import matplotlib
matplotlib.use("Agg")
from matplotlib.ft2font import FT2Font

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT  = ROOT / "data" / "out"
OUT.mkdir(parents=True, exist_ok=True)

SEL_PATH = ROOT / "data" / "out" / "selection_suggestion.json"
if not SEL_PATH.exists():
    print("⚠️ 未找到 selection_suggestion.json，请先运行 scripts/e8_family_rank_sample.py")
    sys.exit(1)

selection = json.loads(SEL_PATH.read_text(encoding="utf-8"))

# 你可把更多 TTF 丢进 fonts/Noto_Sans/ 里（推荐加入 Symbols2/Display）
FONTS_DIR = ROOT / "fonts" / "Noto_Sans"
CANDIDATE_NAMES = [
    "NotoSans-Regular.ttf",
    "NotoSansDisplay-Regular.ttf",
    "NotoSansSymbols2-Regular.ttf",
    "NotoSans-VariableFont_wdth,wght.ttf",
    "NotoSans-Italic-VariableFont_wdth,wght.ttf",
]

font_paths = []
if FONTS_DIR.exists():
    for name in CANDIDATE_NAMES:
        p = (FONTS_DIR / name)
        if p.exists():
            font_paths.append(p.as_posix())

# 系统兜底（可选）
system_guess = [
    r"C:\Windows\Fonts\NotoSans-Regular.ttf",
    r"C:\Windows\Fonts\NotoSansDisplay-Regular.ttf",
    r"C:\Windows\Fonts\seguisym.ttf",
    r"C:\Windows\Fonts\segoeui.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]
for p in system_guess:
    if os.path.exists(p):
        font_paths.append(p)

if not font_paths:
    print("⚠️ 没找到任何字体文件。请把 Noto 的 ttf 放到 fonts/Noto_Sans/。")
    sys.exit(1)

# 读取每个字体的覆盖集合
covers = []  # [(path, set(codepoints))]
for fp in font_paths:
    try:
        ft = FT2Font(fp)
        cmap = set(ft.get_charmap().keys())
        covers.append((fp, cmap))
    except Exception as e:
        print(f"⚠️ 无法读取字体：{fp} ({e})")

# 工具：找第一个能覆盖某码点的字体
def font_for(cp: int):
    for fp, cmap in covers:
        if cp in cmap:
            return fp
    return None

# 工具：列出字符串的所有 NFD 组合符 cp
def combining_marks(s: str):
    nfd = unicodedata.normalize("NFD", s)
    return [ord(c) for c in nfd if unicodedata.category(c) == "Mn"]

# 统计
total = len(selection)
ok = 0
missing_chars = []          # 完全缺字（无任何字体覆盖）
missing_marks_rows = []     # 存在但组合符缺失

# 逐字符检查覆盖
for item in selection:
    ch = item["char"]
    cp = ord(ch)

    # 1) 字符本体
    host_font = font_for(cp)
    host_ok = host_font is not None

    # 2) 组合符清单（如有）
    marks = combining_marks(ch)
    marks_status = []
    for m in marks:
        marks_status.append((m, font_for(m)))

    # 判定
    if not host_ok:
        missing_chars.append({
            "char": ch,
            "codepoint": f"U+{cp:04X}",
            "name": unicodedata.name(ch, ""),
        })
    else:
        # 主体有，但若有某个组合符找不到，也记录
        miss_any_mark = any(fp is None for _, fp in marks_status)
        if miss_any_mark:
            row = {
                "char": ch,
                "codepoint": f"U+{cp:04X}",
                "name": unicodedata.name(ch, ""),
                "missing_marks": "; ".join(
                    f"U+{m:04X}({unicodedata.name(chr(m), '') or 'COMBINING'})"
                    for m, fp in marks_status if fp is None
                )
            }
            missing_marks_rows.append(row)
        else:
            ok += 1

# 统计缺失的具体组合符频次
missing_mark_counter = Counter()
for r in missing_marks_rows:
    for part in r["missing_marks"].split("; "):
        if part:
            code = part.split("(")[0]
            try:
                cp = int(code.replace("U+",""), 16)
                missing_mark_counter[cp] += 1
            except:
                pass

# 写 CSV：完全缺字
miss_glyphs_csv = OUT / "missing_glyphs.csv"
with open(miss_glyphs_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["char","codepoint","name"])
    w.writeheader(); w.writerows(missing_chars)

# 写 CSV：缺失组合符
miss_marks_csv = OUT / "missing_combining_marks.csv"
with open(miss_marks_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["char","codepoint","name","missing_marks"])
    w.writeheader(); w.writerows(missing_marks_rows)

# 写 TXT 报告
report = OUT / "font_coverage_report.txt"
lines = []
lines.append("Miohalo · 字体覆盖侦察器 报告\n")
lines.append(f"候选字符总数: {total}")
lines.append(f"完全可覆盖（含组合符）: {ok}")
lines.append(f"完全缺字 (missing glyphs): {len(missing_chars)}")
lines.append(f"主体有但组合符缺失: {len(missing_marks_rows)}\n")

if missing_mark_counter:
    lines.append("最常缺失的组合符（Top 12）:")
    for cp, cnt in missing_mark_counter.most_common(12):
        nm = unicodedata.name(chr(cp), "") or "COMBINING"
        lines.append(f"  {cnt:>3} × U+{cp:04X}  {nm}")
    lines.append("")
else:
    lines.append("未发现缺失的组合符。🎉\n")

# 建议：根据缺失项提示装哪些 Noto 子字体
suggest = []
if any("RING ABOVE" in r["missing_marks"] for r in missing_marks_rows) or \
   any("ACUTE" in r["missing_marks"] for r in missing_marks_rows) or \
   any("CARON" in r["missing_marks"] for r in missing_marks_rows):
    suggest.append("添加 NotoSansSymbols2-Regular.ttf（含大量组合符/附加符）")
if missing_chars:
    suggest.append("安装 NotoSans-Regular.ttf / NotoSansDisplay-Regular.ttf（静态版更稳）")
if suggest:
    lines.append("建议：")
    for s in suggest:
        lines.append(f" - {s}")
else:
    lines.append("建议：当前字体覆盖良好。")

report.write_text("\n".join(lines), encoding="utf-8")

print("✓ 已写入：", report)
print("✓ 详情 CSV：", miss_glyphs_csv)
print("✓ 组合符缺失：", miss_marks_csv)
print("（把更多 Noto ttf 放进 fonts/Noto_Sans/ 再跑一次，覆盖率会提升。）")
