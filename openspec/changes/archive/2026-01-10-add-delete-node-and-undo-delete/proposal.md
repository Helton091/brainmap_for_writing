# Change: Add node/edge deletion and undo delete

## Why
当前只能删除箭头，不能删除节点；并且删除后无法快速恢复，影响图谱整理效率。

## What Changes
- 增加删除节点能力（删除节点时同时删除其关联箭头）
- 增加删除箭头的统一交互（与现有行为保持一致）
- 增加 Ctrl+Z 撤销“删除操作”（仅覆盖删除，不覆盖编辑/导入/布局等）

## Impact
- Affected specs: event-graph
- Affected code: brainmap_for_writing/ui.py, brainmap_for_writing/core.py (or new core module for undo), tests/
