# Change: Fix executable entrypoint import

## Why
当前将项目打包为可执行文件后，入口模块可能出现“attempted relative import with no known parent package”类错误，导致程序无法启动。

## What Changes
- 入口模块使用绝对导入，确保在可执行文件环境下也能正确加载 UI 启动函数

## Impact
- Affected specs: event-graph
- Affected code: brainmap_for_writing/__main__.py

