## 1. Implementation
- [ ] 1.1 定义删除节点/删除边的统一行为与选择规则
- [ ] 1.2 实现节点删除（含关联边清理）并刷新可见性
- [ ] 1.3 实现删除边（补齐与节点删除一致的交互入口）
- [ ] 1.4 引入撤销栈并支持 Ctrl+Z 撤销最近一次删除
- [ ] 1.5 补充/更新测试覆盖删除与撤销的核心逻辑
- [ ] 1.6 手动回归：删除节点/边、撤销、保存/打开后状态一致

## 2. Validation
- [ ] 2.1 运行 pytest
- [ ] 2.2 运行 openspec validate add-delete-node-and-undo-delete --strict
