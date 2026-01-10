## Context
系统提示词与世界观文档属于项目级的写作设定信息，需要常驻可见且可编辑，并随项目文件一起保存。

## Goals / Non-Goals
- Goals:
  - 左上角固定显示两个文档区域
  - 支持编辑与从 TXT 导入覆盖
  - 随项目 JSON 持久化
- Non-Goals:
  - 版本管理、diff、富文本
  - 多文件引用或目录结构管理

## Decisions
- Decision: 使用 QDockWidget 固定在左侧区域，按添加顺序垂直排列
- Decision: 文档存储在 Graph 顶层字段，序列化为 JSON 的字符串字段
- Decision: TXT 导入采用与现有导入一致的编码尝试（utf-8-sig / gb18030）

## Risks / Trade-offs
- 面板内容较长时会占用屏幕空间，可后续增加折叠/隐藏按钮
