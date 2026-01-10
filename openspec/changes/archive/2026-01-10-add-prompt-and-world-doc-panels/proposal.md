# Change: Add system prompt and world document panels

## Why
写作时需要随时可见与可编辑的系统提示词与世界观文档，作为全局设定与约束；目前应用内缺少这类固定信息区。

## What Changes
- 在主界面左上角增加两个固定面板：System Prompt 与 World Document
- 两个面板内容可直接编辑
- 两个面板支持从 TXT 导入覆盖内容
- 保存/打开项目时一并持久化这两段文本

## Impact
- Affected specs: event-graph
- Affected code: brainmap_for_writing/core.py, brainmap_for_writing/persistence.py, brainmap_for_writing/ui.py, tests/
