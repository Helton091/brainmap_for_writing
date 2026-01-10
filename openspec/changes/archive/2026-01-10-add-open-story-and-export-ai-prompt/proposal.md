# Change: Open linked story txt and export AI-friendly prompt

## Why
用户希望在节点上关联外部故事 txt 后，可以直接从应用内打开该文件以便编辑；同时希望一键导出“世界观一致”的 AI 提示词，把项目级设定与上游节点的关键记忆整合到一个 txt 中，方便交给 AI 创作。

## What Changes
- 若节点已关联故事 txt，右键菜单提供“Open Story TXT”以打开该文件
- 右键菜单新增“Export”操作：将系统提示词、世界观文档、该节点上游节点的所有 memory block，以及本节点 text 组合为 AI 友好提示词并导出为 txt

## Impact
- Affected specs: event-graph
- Affected code: brainmap_for_writing/core.py, brainmap_for_writing/ui.py, tests/
