# ──────────────────────────────────────────────────────────────────────────────
# Miohalo · E8 Family Grouper（只分组，不打分）
# 千夏：哥哥，我把 1252 个孩子都拉回来了，怎么分房间？
# 夜弦：先按“基字母”分族，再按“主特征”分房；不排序、不打分，全交给你挑。
# ──────────────────────────────────────────────────────────────────────────────

import json, csv, pathlib, unicodedata, re
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW  = ROOT / "data" / "raw"
OUT  = ROOT / "data" / "out"
OUT.mkdir(parents=True, exist_ok=True)

# ——— 1) 读取现有 latin_all.json ———
latin = json.loads((RAW / "latin_all.json").read_text(encoding="utf-8"))

# ——— 2) 工具：基字母（去组合符）+ 主特征抽取 ———
MN = {"Mn", "Me"}

FEATURE_PRIORITY = [
    # 形体
    "TURNED", "REVERSED", "SIDEWAYS", "ROTUNDA", "INSULAR", "SCRIPT", "LOOP", "BROKEN",
    # 结构
    "STROKE", "BAR", "SLASH", "HOOK", "TAIL", "HORN", "HORNS", "TOPBAR",
    # 点/符号
    "DOT ABOVE", "DOT BELOW", "DIAERESIS", "ACUTE", "GRAVE", "CIRCUMFLEX", "CARON", "BREVE", "MACRON",
    "RING ABOVE", "OGONEK", "CEDILLA", "TILDE", "DOUBLE GRAVE", "INVERTED BREVE", "LINE BELOW",
    # 组合/连写
    "LIGATURE", "DOUBLE", "TRIPLE", "LETTER AV", "LETTER AY", "LETTER OO", "LETTER DZ", "LETTER LJ", "LETTER NJ",
]

# 可按需在这里把某些名字直接映射到 ASCII 基字母（完全可空，不算“写死”，只是钩子）
ASCII_HINT = {}

name_cache = {}

def u_name(ch:str) -> str:
    if ch in name_cache: return name_cache[ch]
    try:
        name_cache[ch] = unicodedata.name(ch)
    except ValueError:
        name_cache[ch] = ""
    return name_cache[ch]


def base_letter(ch: str) -> str:
    if ch in ASCII_HINT:
        return ASCII_HINT[ch]
    nfd = unicodedata.normalize("NFD", ch)
    stripped = "".join(c for c in nfd if unicodedata.category(c) not in MN)
    b = (stripped or ch).upper()[:1]
    if "A" <= b <= "Z":
        return b
    # 再从名称兜底：LATIN … LETTER X
    m = re.search(r"LATIN (?:SMALL|CAPITAL) LETTER ([A-Z])", u_name(ch))
    return m.group(1) if m else b


def primary_feature(name: str) -> str:
    # 优先匹配 FEATURE_PRIORITY
    for key in FEATURE_PRIORITY:
        if key in name:
            return key
    # 再抓 WITH …
    m = re.search(r"WITH ([A-Z ]+)", name)
    return m.group(1) if m else "NONE"

# ——— 3) 建族（base → feature → members）———
Families: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))

for e in latin:
    ch   = e["char"]
    name = e.get("name") or u_name(ch)
    base = base_letter(ch)
    feat = primary_feature(name)
    item = {
        "char": ch,
        "codepoint": e.get("codepoint"),
        "name": name,
        "case": ("U" if ch.isupper() else ("L" if ch.islower() else "?")),
    }
    Families[base][feat].append(item)

# ——— 4) 导出：不排序、不打分 ———
# 4.1 families.json（层级：base → feature → members[]）

families_out = []
for base in sorted(Families.keys()):
    features = []
    for feat, members in sorted(Families[base].items()):
        # 成员保持原始输入顺序；不排序
        features.append({
            "feature": feat,
            "size": len(members),
            "members": members,
        })
    families_out.append({
        "base": base,
        "size": sum(len(v) for v in Families[base].values()),
        "features": features,
    })

(OUT / "families.json").write_text(
    json.dumps(families_out, ensure_ascii=False, indent=2), encoding="utf-8"
)

# 4.2 char_groups.csv（扁平视图：便于筛选/打印）
with open(OUT / "char_groups.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["base", "feature", "size", "chars", "codepoints"])
    for base in sorted(Families.keys()):
        for feat, members in sorted(Families[base].items()):
            w.writerow([
                base,
                feat,
                len(members),
                "".join(m["char"] for m in members),
                " ".join(m.get("codepoint","?") for m in members)
            ])

# 4.3 char_list.txt（全量清单，供人工视检）
with open(OUT / "char_list.txt", "w", encoding="utf-8") as f:
    for base in sorted(Families.keys()):
        f.write(f"# BASE {base}\n")
        for feat, members in sorted(Families[base].items()):
            f.write(f"## {feat} ({len(members)})\n")
            for m in members:
                f.write(f"{m['char']}\t{m.get('codepoint','?')}\t{m['name']}\t{m['case']}\n")
            f.write("\n")

print("✓ 分组完成（无排序/无打分）：families.json, char_groups.csv, char_list.txt → data/out/")
print("千夏：我拿纸来印。\n夜弦：每个家都有自己的窗子，慢慢挑，慢慢亮。")