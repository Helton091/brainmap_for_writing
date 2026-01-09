# Change: Render nodes as circles with hover tooltips

## Why
在节点数量变多时，节点内部文字会造成画布噪声，降低结构阅读效率。
将节点简化为小圆点并仅显示时间，可以让用户先专注于事件的时间线与关系；需要查看内容时再通过悬停提示快速阅读。

## What Changes
- 节点以小圆圈渲染，默认隐藏正文
- 节点仅显示日期（无日期节点显示占位符）
- 鼠标悬停节点时，以提示信息显示完整事件文本
- 提供用户使用说明书

## Impact
- Affected specs: event-graph
- Affected code: brainmap_for_writing/ui.py
