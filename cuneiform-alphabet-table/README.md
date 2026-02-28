# 楔形文字与 26 个英文字母对照表（草案）

这个目录现在先做两件事：
1. 自动获取 Unicode 楔形文字库；
2. 自动生成 A-Z 的首轮候选，方便我们人工二次筛选。

## 快速开始

```bash
python cuneiform-alphabet-table/scripts/select_cuneiform.py --build-library --select
```

执行后会生成：

- `data/raw/cuneiform_unicode_library.json`：完整楔形字符库（Unicode 三个楔形区块）。
- `data/raw/cuneiform_unicode_library.csv`：同库的 CSV 版本。
- `data/processed/az_cuneiform_selection.json`：A-Z 自动初选结果。
- `data/processed/az_cuneiform_selection.csv`：初选结果 CSV。
- `data/processed/az_cuneiform_selection.md`：可直接阅读的表格。

## 筛选策略（v1）

当前脚本的自动策略：

1. 在 Unicode 名称里查找 `SIGN` 且包含对应拉丁字母 token（例如 `A`）。
2. 候选按以下规则排序：
   - 优先 `... SIGN X` 的精确尾部匹配；
   - 再选名称更短的；
   - 最后按名称字典序稳定输出。
3. 若某字母没匹配到，就标记 `missing`，留给手工挑选。

> 说明：这是“起步筛选器”，不是最终定稿。最终还要按“易写、易记、区分度”做人工评审。

## 下一步

- 先人工复核 A、E、I、O、U（元音优先）。
- 建立“拒绝清单”（形近/难写/语义不合）。
- 在脚本里加入人工白名单与黑名单参数，做可复现迭代。
