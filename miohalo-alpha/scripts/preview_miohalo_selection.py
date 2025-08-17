# preview_miohalo_selection.py — Miohalo · E8 字魂墙（智能字体 fallback + 纯字形）
# ─────────────────────────────────────────────────────────────────────────────
# 哥哥：这是我们一起打磨的最终版。逻辑保持“零写死分组”，只靠 Unicode 分解与名称推断骨架。
# 妹妹：而且加上黑名单、分组预览、清单导出和按字符真实覆盖挑字体，不会出现方块。
# 哥哥：注释里我会用“哥哥：/妹妹：”对话把思路讲清楚，方便以后继续改魔法。
# ─────────────────────────────────────────────────────────────────────────────
# 用法：
#   python scripts/preview_miohalo_selection.py
# 说明：
#   - 自动扫描 fonts/Noto_Sans/ 下的 ttf/otf，逐字选择“真支持该字符”的字体绘制，杜绝方块。
#   - 只画大字形，无任何编码/网格背景；更高 DPI 与更合理行距。
#   - 建议放入：NotoSans-Regular.ttf、NotoSansDisplay-Regular.ttf、
#               NotoSansSymbols2-Regular.ttf、NotoSansSC-Regular.otf（或 CJK 变体）

import os, sys, json, pathlib, unicodedata as ud, re
import matplotlib
matplotlib.use("Agg")  # 哥哥：我们只生成图片，不弹出窗口。
from matplotlib import font_manager
import matplotlib.pyplot as plt
from matplotlib.ft2font import FT2Font
from matplotlib.font_manager import FontProperties
from functools import lru_cache
from collections import defaultdict

# ───────────────── 路径
# 妹妹：这些是约定的项目结构，跟着用就好。
ROOT = pathlib.Path(__file__).resolve().parent.parent
SELECTION  = ROOT / "data" / "out" / "selection_suggestion.json"
OUTTXT     = ROOT / "data" / "out" / "char_list.txt"
OUTCSV     = ROOT / "data" / "out" / "char_groups.csv"
OUTPNG     = ROOT / "preview.png"
FONTS_DIR  = ROOT / "fonts" / "Noto_Sans"
REJECT_TXT = ROOT / "data" / "reject.txt"

# ───────────────── 画面参数 / 行为开关
# 哥哥：想要紧凑一点还是松一点，这里随时改。
GROUP_BY_SKELETON = True   # True=把相似骨架的放一起
COLS        = 10           # 每行字数
GLYPH_FSIZE = 44           # 字号
LINE_PAD    = 1.10         # 行距系数（越大越疏）
Y_SHIFT     = 0.00         # 竖向微调
DPI         = 320          # 输出分辨率
MARGIN_T    = 0.92         # 顶部留白
MARGIN_B    = 0.06         # 底部留白
MARGIN_L    = 0.04
MARGIN_R    = 0.96

# ───────────────── 读取候选集
if not SELECTION.exists():
    print("⚠️ 未找到 data/out/selection_suggestion.json（先跑 scripts/e8_family_rank_sample.py）")
    sys.exit(1)

# 妹妹：候选既支持 ["字", ...] 也支持 [{"char":"字"}, ...]。
raw = json.loads(SELECTION.read_text(encoding="utf-8"))
if not raw:
    print("⚠️ 候选集为空"); sys.exit(1)

chars = []
for it in raw:
    ch = it.get("char", "") if isinstance(it, dict) else str(it)
    if ch:
        chars.append(ch)

# ───────────────── 黑名单过滤（data/reject.txt）
# 哥哥：不想要的字直接写进 reject.txt（每行一个），这里自动剔除。
REJECT = set()
if REJECT_TXT.exists():
    REJECT = set(REJECT_TXT.read_text(encoding="utf-8").split())
if REJECT:
    before = len(chars)
    chars = [ch for ch in chars if ch not in REJECT]
    print(f"• 黑名单过滤：移除 {before - len(chars)} 个字符")

# ───────────────── 收集字体文件
# 妹妹：优先项目内 fonts/Noto_Sans/，其次系统路径兜底。
CANDIDATE_NAMES = [
    "NotoSans-Regular.ttf",
    "NotoSansDisplay-Regular.ttf",
    "NotoSansSymbols2-Regular.ttf",
    "NotoSansSC-Regular.otf",                # CJK（如有）
    "NotoSans-VariableFont_wdth,wght.ttf",
    "NotoSans-Italic-VariableFont_wdth,wght.ttf",
]
font_paths = []
if FONTS_DIR.exists():
    for name in CANDIDATE_NAMES:
        fp = (FONTS_DIR / name)
        if fp.exists():
            font_paths.append(fp.as_posix())

# 系统猜测（可按平台增减）
system_guess = [
    r"C:\Windows\Fonts\NotoSans-Regular.ttf",
    r"C:\Windows\Fonts\NotoSansDisplay-Regular.ttf",
    r"C:\Windows\Fonts\seguisym.ttf",
    r"C:\Windows\Fonts\segoeui.ttf",
    r"C:\Windows\Fonts\msyh.ttc",
    "/System/Library/Fonts/Supplemental/NotoSans.ttc",
    "/System/Library/Fonts/Supplemental/AppleSymbols.ttf",
    "/System/Library/Fonts/PingFang.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]
for p in system_guess:
    if os.path.exists(p):
        font_paths.append(p)

# 去重，保持顺序
seen = set()
font_paths = [p for p in font_paths if (p not in seen and not seen.add(p))]
if not font_paths:
    print("⚠️ 没找到任何字体文件。请把 Noto 的 ttf 放到 fonts/Noto_Sans/ 再试。")
    sys.exit(1)

# 妹妹：注册给 matplotlib，以便按 fname 精确指定。
for p in font_paths:
    try:
        font_manager.fontManager.addfont(p)
    except Exception:
        pass

# ───────────────── 建立“字符覆盖”与选字函数
# 哥哥：我们读取每个字体的 charmap，真正能覆盖才用，避免画出方块。
cover_maps = []
for p in font_paths:
    try:
        f = FT2Font(p)
        cmap = set(f.get_charmap().keys())
        if cmap:
            cover_maps.append((p, cmap))
        else:
            print(f"• 跳过（无 charmap）：{p}")
    except Exception as e:
        print(f"• 跳过（读取失败）：{p}  —— {e.__class__.__name__}")

# 控制码与变体选择器（不计入覆盖判断）
IGNORES   = {0x200D, 0x200C, 0x200B, 0x2060}  # ZWJ/ZWNJ/ZWSP/WJ
VARIATION = set(range(0xFE00, 0xFE10)) | set(range(0xE0100, 0xE01F0))

def normalize_cps(s: str):
    out = []
    for ch in s:
        cp = ord(ch)
        if cp in IGNORES or cp in VARIATION:
            continue
        out.append(cp)
    return out

def supports_sequence(cmap: set, s: str) -> bool:
    cps = normalize_cps(s)
    if not cps:
        return True
    return all(cp in cmap for cp in cps)

@lru_cache(maxsize=4096)
def pick_font_for_text(s: str):
    # 妹妹：逐个尝试字体，谁能“真覆盖”就用谁。
    for path, cmap in cover_maps:
        if supports_sequence(cmap, s):
            return FontProperties(fname=path)
    return None  # 真缺失：不画

# ───────────────── 自适应相似归类（零写死）
# 哥哥：只用 Unicode 的正规分解 + 名称抽取，自动得到骨架（A–Z），推不出就归入 #。
NAME_RE = re.compile(r"LATIN (CAPITAL|SMALL) LETTER ([A-Z])")

def get_base(ch: str) -> str:
    """自动推断字符骨架：优先 NFKD 去附标后取首个 A–Z；否则从 Unicode 名称里抓 LETTER X；否则用 #"""
    core = "".join(c for c in ud.normalize("NFKD", ch) if ud.category(c) != "Mn")
    if core:
        c0 = core[0].upper()
        if "A" <= c0 <= "Z":
            return c0
    m = NAME_RE.search(ud.name(ch, ""))
    if m:
        return m.group(2)
    return "#"

# 妹妹：附标类别的粗排序，让“母本 → 轻附标 → 强改形”更有节律。
MARK_ORDER = [
    "ACUTE","GRAVE","CIRCUMFLEX","CARON","TILDE","MACRON","BREVE","RING",
    "DOT","DIAERESIS","HORN","HOOK","CEDILLA","OGONEK","STROKE","BAR","SLASH",
]

def mark_class(name: str) -> int:
    for i, key in enumerate(MARK_ORDER):
        if key in name:
            return i + 1
    return 0

def sort_key(ch: str):
    name = ud.name(ch, "")
    return (
        int(" WITH " in name),   # 0=母本，1=带附标/变体
        mark_class(name),        # 附标类别次序
        name,                    # 名称
        ch                       # 字符本身
    )

if GROUP_BY_SKELETON:
    # 哥哥：分桶、桶内排序、A–Z 顺序展开。
    buckets = defaultdict(list)
    for ch in chars:
        buckets[get_base(ch)].append(ch)
    for k in buckets:
        buckets[k].sort(key=sort_key)
    ordered_keys = [k for k in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if k in buckets] + \
                   [k for k in buckets if k not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]

    grouped_chars = []
    print("\n── 分组预览（骨架 → 成员示例）")
    for k in ordered_keys:
        members = buckets[k]
        grouped_chars.extend(members)
        preview = " ".join(members[:12])
        print(f"[{k}] x{len(members)} : {preview}{' …' if len(members)>12 else ''}")
    chars = grouped_chars

# ───────────────── 画布尺寸
N = len(chars)
COLS = max(1, int(COLS))
ROWS = (N + COLS - 1) // COLS
# 妹妹：高度根据字号与行距推导，防止过密或过稀。
FIG_W = COLS * 1.0
FIG_H = max(1.0, ROWS * (GLYPH_FSIZE / 72.0) * LINE_PAD)

fig = plt.figure(figsize=(FIG_W, FIG_H))
plt.axis('off')
fig.subplots_adjust(top=MARGIN_T, bottom=MARGIN_B, left=MARGIN_L, right=MARGIN_R)

# ───────────────── 输出清单并绘制
OUTTXT.parent.mkdir(parents=True, exist_ok=True)
with OUTTXT.open("w", encoding="utf-8") as ftxt, OUTCSV.open("w", encoding="utf-8") as fcsv:
    fcsv.write("index,char,codepoint,name,group\n")
    missing = []

    for idx, ch in enumerate(chars):
        r = idx // COLS
        c = idx % COLS
        x = (c + 0.5) / COLS
        y = 1.0 - ((r + 0.5) / max(1, ROWS))

        fp = pick_font_for_text(ch)
        if fp is None:
            # 哥哥：极少数字符所有候选字体都不支持，就报告并跳过。
            missing.append(ch)
            continue

        code  = f"U+{ord(ch):04X}"
        name  = ud.name(ch, "<unknown>")
        group = get_base(ch) if GROUP_BY_SKELETON else ""

        # 控制台打印（便于定位删除/调整）
        print(f"[{idx}] {ch}  {code}  {name}  [{group}]")

        # 清单文件
        ftxt.write(f"[{idx}] {ch}  {code}  {name}  [{group}]\n")
        fcsv.write(f"{idx},{ch},{code},{name},{group}\n")

        # 绘制大字形
        plt.text(x, y + Y_SHIFT, ch,
                 ha='center', va='center',
                 fontsize=GLYPH_FSIZE,
                 fontproperties=fp)

# 妹妹：标题里会自动显示 n=当前数量。
plt.suptitle(f"Miohalo · E8 Resonant Selection  (n={N})", fontsize=14)
plt.savefig(OUTPNG.as_posix(), dpi=DPI)
print(f"\n✓ 纯字形预览已生成：{OUTPNG}")
print(f"✓ 清单已写出：{OUTTXT}")
print(f"✓ 分组明细：{OUTCSV}")
if 'missing' in locals() and missing:
    sample = "".join(missing[:40])
    print(f"⚠️ {len(missing)} 个字符在候选字体中找不到，已跳过。示例：{sample}")
