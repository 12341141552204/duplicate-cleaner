<div align="center">

# 🗑️ PhotoDedupe

### 摄影师专用去重工具 — 按内容比对 · 连拍清理 · 硬盘释放

A duplicate file cleaner designed for photographers: find identical RAW/JPG by content hash, batch clean up duplicate shots.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-green.svg)](https://github.com/12341141552204/duplicate-cleaner)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/12341141552204/duplicate-cleaner)](https://github.com/12341141552204/duplicate-cleaner)

</div>

## 🎯 为什么摄影师需要这个工具

一场活动拍了 500 张，连拍导致几十张内容几乎相同？修图导出了两个版本分不清？硬盘被重复照片占满？

**PhotoDedupe 帮你：**
- 🔍 按文件内容（MD5）精确比对，找到完全相同的照片
- 📊 一键统计重复照片占用的空间
- 🗑️ 安全删除：先预览再操作，误删可恢复（回收站）
- 📋 导出重复清单，方便检查

## ✨ 功能特性

| 功能 | 说明 |
|---|---|
| 精确扫描 | 按 MD5 内容比对，文件名不同也能找到 |
| 递归扫描 | 自动扫描子文件夹 |
| 预览模式 | 先看重复列表，不删除任何文件 |
| 安全删除 | 删除到回收站，不是永久删除 |
| 导出报告 | 重复清单导出为文本文件 |
| 空间统计 | 显示重复文件占用了多少硬盘空间 |

## 📦 安装

```bash
git clone https://github.com/12341141552204/duplicate-cleaner.git
# 无需额外依赖
```

## 🚀 使用方法

### 1. 扫描重复照片

```bash
# 扫描整个文件夹
python main.py scan "D:\婚礼拍摄\2026-08-29"

# 递归扫描子文件夹
python main.py scan "D:\婚礼拍摄" --recursive
```

### 2. 预览删除（安全模式）

```bash
# 只看不删，确认重复列表
python main.py delete "D:\婚礼拍摄\2026-08-29" --dry-run
```

### 3. 执行删除

```bash
# 删除重复文件（保留每个组的第一张）
python main.py delete "D:\婚礼拍摄\2026-08-29"
```

### 4. 导出报告

```bash
python main.py export "D:\婚礼拍摄" -o "重复清单.txt"
```

## 📖 命令参考

| 命令 | 用途 |
|---|---|
| `scan <目录>` | 扫描重复文件 |
| `scan <目录> --recursive` | 递归扫描 |
| `delete <目录> --dry-run` | 预览删除 |
| `delete <目录>` | 执行删除 |
| `export <目录> -o <文件>` | 导出报告 |

## 💡 使用场景

| 场景 | 操作 |
|---|---|
| 连拍清理 | `scan` → `delete --dry-run` → `delete` |
| 硬盘清理 | `scan` + `--recursive` 全盘扫描 |
| 修图去重 | `scan` 找出重复导出的图片 |
| 交接前检查 | `export` 导出清单确认 |

## 🤝 贡献

欢迎提交 Issue 和 PR！请阅读 [贡献指南](CONTRIBUTING.md)。

## 💖 赞助

如果这个工具帮你释放了硬盘空间，请考虑赞助：

| 方案 | 月费 | 权益 |
|---|---|---|
| 🥤 随手一杯 | ¥5 | README 署名 + 月度进展 |
| 🚀 催更选手 | ¥15 | 提前体验 + 优先排功能 |
| 👑 金主爸爸 | ¥50 | 功能优先建议 + 项目挂名 |

👉 [爱发电赞助](https://afdian.com/a/JingJingZ)

## 📄 许可证

[MIT License](LICENSE) - 自由使用，欢迎商用
