# Change: Add node color, short note, and collapse/expand

## Why
当节点数量增多时，用户需要快速区分不同类型事件，并在不阅读长正文的情况下记录关键信息。
同时，时间链很长时需要“折叠/展开”来聚焦当前关注的片段。

## What Changes
- 节点支持设置颜色，用于图例与分类
- 节点支持设置极简文字注释，并在节点上显示
- 节点支持展开/隐藏其后续链路（按有向边）
- 保存/加载需包含颜色、注释与折叠状态

## Impact
- Affected specs: event-graph
- Affected code: core model, persistence, UI rendering and interaction
