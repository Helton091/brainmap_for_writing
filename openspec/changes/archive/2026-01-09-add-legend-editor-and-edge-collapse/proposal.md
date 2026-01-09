# Change: Legend editor and edge-level collapse/expand

## Why
用户需要显式维护图例（颜色含义），并在复杂分叉链路中按“边”折叠部分路径来聚焦。

## What Changes
- 右上角提供图例编辑：为每种颜色设置极简文字说明
- hide/expand 从“节点”移动到“箭头（边）”
- 在每条边上渲染明显的加号/减号按钮用于折叠/展开
- 当某条边被折叠时，加号旁显示指向节点的极简注释

## Impact
- Affected specs: event-graph
- Affected code: core model, persistence, visibility, UI
