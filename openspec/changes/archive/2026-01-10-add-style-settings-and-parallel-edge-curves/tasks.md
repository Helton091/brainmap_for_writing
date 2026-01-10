## 1. Implementation
- [ ] 1.1 设计并实现“显示/外观设置”UI（合并日期/时间显示与样式）
- [ ] 1.2 将设置落地到渲染层：节点半径、边线宽、箭头尺寸随之变化
- [ ] 1.3 实现平行边检测与弯曲渲染，避免 A->B 多边重合
- [ ] 1.4 补充测试：平行边偏移计算、设置更新对几何参数影响
- [ ] 1.5 手动回归：设置修改即时生效；保存/打开不崩溃；平行边可区分

## 2. Validation
- [ ] 2.1 运行 pytest
- [ ] 2.2 运行 openspec validate add-style-settings-and-parallel-edge-curves --strict
