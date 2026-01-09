# Change: Improve arrow direction, layout spacing, tooltip, and zoom

## Why
当前画布在节点较多时可读性不足：箭头方向不够显著、节点纵向分布偏散、提示文本不够醒目、缺少整体缩放影响浏览效率。

## What Changes
- 增强箭头方向性（更明显的箭头头部）
- 调整默认布局以减少节点生成时的竖直间距
- 优化悬停提示：更大字号、提示框更接近正方形
- 支持画布整体放缩（鼠标/快捷方式）

## Impact
- Affected specs: event-graph
- Affected code: brainmap_for_writing/ui.py, brainmap_for_writing/layout.py
