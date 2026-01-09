# Project Context

## Purpose
开发一款写作辅助软件，用“节点”记录事件及其逻辑/先后关系，帮助用户把分散的事件记录组织成可推演的结构。

核心目标：
- 用户可自由创建节点，录入事件时间与事件内容
- 支持从 txt 导入，自动生成节点（必须含有日期）
- 在画布上以可视化方式排布节点，并用有向箭头表达节点关系
- 允许用户拖拽移动节点位置，形成自己的叙事结构

## Tech Stack
- Language: Python
- UI: PySide6 (Qt) 桌面应用（可拖拽节点与连线）
- Data: JSON 文件本地持久化（节点、关系、布局坐标）
- Testing: pytest（解析、导入、序列化与布局计算）

## Project Conventions

### Code Style
- 使用现代 Python（类型标注用于核心模型与公共函数）
- 业务逻辑与 UI 分层：UI 只负责交互与渲染，核心逻辑可独立测试
- 文件路径使用 pathlib
- 文本编码统一使用 UTF-8
- 错误信息对用户友好（导入失败要指出行号/位置与原因）

### Architecture Patterns
- 模型层：Node、Edge、Graph、Layout（坐标）
- 导入层：txt 解析为中间结构，再转换为模型
- 持久化层：Graph/布局的 load/save
- UI 层：画布（QGraphicsView/Scene）渲染节点与箭头，支持拖拽与选择

### Testing Strategy
- 单元测试：txt 导入解析（包括日期块、无日期块、空行等边界）
- 回归测试：同一输入导出/保存结果应稳定可复现
- 关键逻辑（布局、序列化）必须可在无 UI 环境下测试

### Git Workflow
- 小步提交，保持主分支可运行
- 建议使用 Conventional Commits（feat/fix/refactor/test/chore）

## Domain Context
- 节点（Node）：用户创建的事件记录，包含可选日期与正文文本
- 关系（Edge）：节点之间的有向连线，表达先后或因果等逻辑关系
- 画布（Canvas）：节点的二维布局空间；“越晚时间的节点尽可能靠右”是默认布局规则
- 导入 txt：以 `【YYYY.MM.DD】` 作为日期块起始标记，直到下一个日期标记之前的文本属于该日期节点；不带日期标记的文本也应生成无日期节点

## Important Constraints
- 核心功能离线可用，不依赖网络服务
- Windows 优先，但路径/编码/换行处理需跨平台
- 默认布局是辅助，用户始终可以手动拖拽调整

## External Dependencies
- 无外部服务依赖
