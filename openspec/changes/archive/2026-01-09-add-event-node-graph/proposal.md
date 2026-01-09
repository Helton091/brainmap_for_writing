# Change: Add event node graph editor with txt import

## Why
把事件写成线性文本后，很难快速看清先后与逻辑关系。
通过可拖拽的节点图谱与有向连线，用户能更直观地组织叙事结构，并逐步完善事件链。

## What Changes
- 提供节点画布：创建节点、编辑内容、拖拽移动
- 节点支持可选事件日期与事件文本
- 支持从 txt 文件导入：按示例格式解析日期块并自动生成节点
- 提供有向箭头：在节点之间建立/删除先后关系
- 提供本地持久化：保存/加载节点、关系与布局坐标

## Impact
- Affected specs: event-graph
- Affected code: 新增 Python 桌面应用与导入/持久化模块（待实现）
