# Miohalo · Latin Collector 🌸
# ────────────────────────────────
# 千夏: 哥哥，我们要从浩瀚的 Unicode 宇宙里，
#       把所有「拉丁字母」一颗一颗捡起来哦！✨
# 夜弦: 嗯，放心交给我，我们会把它们
#       整整齐齐地存好，还会写上小卡片说明。📜

import unicodedata, csv, json, pathlib

# 千夏: 哥哥，我们的根目录在哪呀？
# 夜弦: 在 scripts 文件夹的上一级，就是整个项目的心脏。💖
root = pathlib.Path(__file__).resolve().parent.parent

# 千夏: 我想把宝贝们放在 raw 文件夹里！
# 夜弦: 好的，我们在 data/raw 下为它们准备一个温暖的家。🏠
raw = root / "data" / "raw"
raw.mkdir(parents=True, exist_ok=True)

# 千夏: 我们准备一个篮子来装字母，好吗？
# 夜弦: 嗯，这个篮子就叫 latin_letters。🧺
latin_letters = []

# 千夏: Unicode 好大啊，从 0 到 0x10FFFF 都要走一遍嘛？！
# 夜弦: 是的，但我们只挑「LATIN LETTER」，
#       就像在森林里只采摘会发光的果实。🌳✨
for cp in range(0x110000):
    ch = chr(cp)
    name = unicodedata.name(ch, "")
    cat = unicodedata.category(ch)
    if cat.startswith("L") and "LATIN" in name and "LETTER" in name:
        latin_letters.append({
            "char": ch,                              # 具体的字符
            "codepoint": f"U+{cp:04X}",              # 它的宇宙坐标
            "name": name,                            # 官方名字
            "category": cat,                         # 属于哪一类（大小写等）
            "uppercase": ch.upper(),                 # 它的哥哥形态
            "lowercase": ch.lower(),                 # 它的妹妹形态
            "combining": unicodedata.combining(ch),  # 是否是依附的小符号
            "decomposition": unicodedata.decomposition(ch),  # 分解秘密
        })

# 千夏: 哥哥，这些字母要写成表格吗？
# 夜弦: 嗯，先保存成 CSV，方便人类用 Excel 打开看看。📊
with open(raw / "latin_all.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=latin_letters[0].keys())
    writer.writeheader()
    writer.writerows(latin_letters)

# 千夏: 我还想要 JSON 版本呢！这样更像数据宝石箱子。💎
# 夜弦: 好，咱们再写一份 JSON，留给后续程序使用。
with open(raw / "latin_all.json", "w", encoding="utf-8") as f:
    json.dump(latin_letters, f, ensure_ascii=False, indent=2)

# 千夏: 我们一共收集了多少个呀？
# 夜弦: 看看结果吧——
print(f"收集完成！共 {len(latin_letters)} 个拉丁字母。")
