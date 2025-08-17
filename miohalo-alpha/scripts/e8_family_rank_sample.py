# Miohalo · E8 Family Ranker
# 千夏: 哥哥，我把 1252 个孩子都拉回来了，怎么分房间呢？
# 夜弦: 先按“基字母”分族，再听一耳朵谁更合 E8 的和声。

import json, csv, pathlib, unicodedata, re
from collections import defaultdict, Counter

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW  = ROOT / "data" / "raw"
OUT  = ROOT / "data" / "out"
OUT.mkdir(parents=True, exist_ok=True)

# ——— 1) 加载原始 latin 列表 ———
latin = json.loads((RAW / "latin_all.json").read_text(encoding="utf-8"))

# ——— 2) 工具：去掉组合符，得到“基字母”（NFD 再剔除 Mn）
def base_letter(ch: str) -> str:
    nfd = unicodedata.normalize("NFD", ch)
    return "".join(c for c in nfd if unicodedata.category(c) != "Mn")

# ——— 3) 特征模板（8维 E8 影子）———
V_SYM_SET_U = set("AHIMOTUVWXY")
V_SYM_SET_L = set("ahimotuvwx y".replace(" ", "")) | set("io")
H_SYM_SET   = set("oOxX")
ASC_SET     = set("bdfhklt")
DES_SET     = set("gjpqy")
LOOP_SET    = set("abdegopqABDOPQR")

DIACRITIC_KEYS = {
    "ACUTE": "acute", "GRAVE":"grave", "CIRCUMFLEX":"circumflex", "CARON":"caron",
    "TILDE":"tilde", "MACRON":"macron", "BREVE":"breve", "DOT":"dot",
    "RING":"ring", "OGONEK":"ogonek", "CEDILLA":"cedilla", "HORN":"horn",
    "DIAERESIS":"diaeresis"
}

def letter_features(ch: str, name: str):
    base = base_letter(ch)
    base0 = base.lower()[:1] if base else ch.lower()
    is_upper = ch.isupper()

    # 对称近似
    v_sym = 1 if ((is_upper and base0.upper() in V_SYM_SET_U) or
                  (not is_upper and base0 in V_SYM_SET_L)) else 0
    h_sym = 1 if (base0 in "ox") else 0

    asc = 1 if base0 in ASC_SET else 0
    des = 1 if base0 in DES_SET else 0
    loop = 1 if base0 in set(c.lower() for c in LOOP_SET) else 0

    # 结构改动：STROKE/BAR/HOOK 等
    structural = 1 if re.search(r"\b(STROKE|BAR|HOOK)\b", name) else 0

    # 组合符复杂度：从名字解析
    dia_count = 0
    dia_vec = Counter()
    for key, tag in DIACRITIC_KEYS.items():
        if key in name:
            dia_vec[tag] += 1
            dia_count += 1
    # 再从分解看一眼（NFD -> Mn）
    nfd = unicodedata.normalize("NFD", ch)
    dia_count += sum(1 for c in nfd if unicodedata.category(c) == "Mn")

    # 压缩一个“复杂度”标量（平方和开根）
    dia_complex = (sum(v*v for v in dia_vec.values())) ** 0.5

    return {
        "v_sym": v_sym,
        "h_sym": h_sym,
        "asc": asc,
        "des": des,
        "loop": loop,
        "structural": structural,
        "dia_count": dia_count,
        "dia_complex": float(dia_complex),
        "base": base0
    }

# ——— 4) 权重（可调）———
W = {
    "v_sym": 0.30,
    "h_sym": 0.10,
    "asc":   0.05,
    "des":   0.05,
    "loop":  0.10,
    "structural": 0.12,      # 喜欢带“划/钩”的异色音可拉高
    "dia_count":  -0.12,     # 组合符过多降权
    "dia_complex": -0.08
}

def score(feat):
    return sum(W[k] * feat[k] for k in W)

# ——— 5) 建族 + 打分 ———
families = defaultdict(list)

for e in latin:
    ch   = e["char"]
    name = e["name"]
    f = letter_features(ch, name)
    s = score(f)
    item = {
        "char": ch,
        "codepoint": e["codepoint"],
        "name": name,
        "is_upper": ch.isupper(),
        "features": f,
        "score": round(s, 6)
    }
    families[f["base"]].append(item)

# ——— 6) 导出家族与候选清单 ———
# families.json
fam_out = []
for base, members in sorted(families.items()):
    fam_out.append({
        "base": base,
        "size": len(members),
        "members": sorted(members, key=lambda x: x["score"], reverse=True)
    })
(OUT / "families.json").write_text(json.dumps(fam_out, ensure_ascii=False, indent=2), encoding="utf-8")

# ranked_candidates.csv（全体按分数降序）
flat = []
for base, members in families.items():
    for m in members:
        flat.append({
            "base": base,
            "char": m["char"],
            "codepoint": m["codepoint"],
            "name": m["name"],
            "score": m["score"]
        })
flat.sort(key=lambda x: x["score"], reverse=True)

with open(OUT / "ranked_candidates.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(flat[0].keys()))
    w.writeheader(); w.writerows(flat)

# ——— 7) 给一个“选型建议”——按目标规模挑代表 ———
TARGET = 216         # 你可改成 144 / 192 / 288 …
PER_FAMILY = 4       # 每族最多选多少（先大小写各1，再两枚附加符代表）
selection = []
for fam in fam_out:
    picks = []
    uppers = [m for m in fam["members"] if m["is_upper"]]
    lowers = [m for m in fam["members"] if not m["is_upper"]]
    if uppers: picks.append(uppers[0])
    if lowers: picks.append(lowers[0])
    # 继续从剩余里选高分者到 PER_FAMILY
    remain = [m for m in fam["members"] if m not in picks]
    remain.sort(key=lambda x: x["score"], reverse=True)
    for m in remain[:max(0, PER_FAMILY - len(picks))]:
        picks.append(m)
    selection.extend(picks)

# 全体限额到 TARGET
selection.sort(key=lambda x: x["score"], reverse=True)
selection = selection[:TARGET]

(OUT / "selection_suggestion.json").write_text(
    json.dumps(selection, ensure_ascii=False, indent=2), encoding="utf-8"
)

print(f"✓ Families: {len(families)} bases")
print(f"✓ Ranked list → {OUT/'ranked_candidates.csv'}")
print(f"✓ Suggestion ({TARGET}) → {OUT/'selection_suggestion.json'}")
print("千夏: 先听一版和声吧！")
print("夜弦: 权重在脚本 W 里，随时调，直到它会发光。")
