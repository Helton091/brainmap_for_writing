# Change: Add node memory block, story link, and minimizable documents

## Why
世界观文档与系统提示词需要在写作时可随时查看但不应占用过多空间；同时每个节点需要“概述性记忆”与外部故事 txt 的关联能力，便于后续 AI 创作时快速检索。

## What Changes
- 系统提示词与世界观文档面板支持最小化/展开
- 每个节点新增 memory block 字段，用于概述节点故事
- 每个节点可关联一个故事 txt 文件，仅保存路径，不存储文件内容

## Impact
- Affected specs: event-graph
- Affected code: brainmap_for_writing/core.py, brainmap_for_writing/ui.py, tests/
