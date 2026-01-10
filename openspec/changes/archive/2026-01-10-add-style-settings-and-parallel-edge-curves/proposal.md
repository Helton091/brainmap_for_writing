# Change: Add style settings and parallel edge curves

## Why
当前节点与箭头样式固定，用户无法按个人偏好调整可读性；同时当 A->B 存在多条相同有向边时会重合，难以辨识与点击。

## What Changes
- 新增“显示/外观设置”入口：合并时间显示设置与外观设置（节点大小、箭头粗细等）
- 支持多条相同有向边 A->B 时自动弯曲，避免重合并提升辨识度

## Impact
- Affected specs: event-graph
- Affected code: brainmap_for_writing/ui.py, (optional) new module for edge geometry
