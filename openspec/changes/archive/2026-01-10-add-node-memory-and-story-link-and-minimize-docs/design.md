## Context
节点正文是“原始记录”，memory block 是“概述性摘要”；故事 txt 属于外部文件，应用只保存其访问方式以避免重复存储。

## Goals / Non-Goals
- Goals:
  - 文档面板可最小化以节省屏幕空间
  - memory block 可编辑并随项目保存
  - 节点故事 txt 以路径关联并随项目保存
- Non-Goals:
  - 存储/同步故事 txt 的内容
  - 打开/编辑外部 txt 的内置编辑器

## Decisions
- Decision: memory block 与 story_txt_path 作为 Node 字段写入项目 JSON
- Decision: story_txt_path 仅存字符串路径，不读取文件内容
- Decision: 文档面板最小化仅影响 UI 展示，不影响保存内容
