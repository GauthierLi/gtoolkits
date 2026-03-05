# GTools 工具模块语义映射表

> 本文档维护工具模块关键词映射关系，用于 AI 路由决策。
> 更新时间：2026-03-04

## 工具模块列表

| 模块名 | 关键词 | 描述 | skill.md |
|--------|--------|------|----------|
| backup_openclaw_memory | 备份、恢复、OpenClaw、记忆、迁移、backup、restore、memory | OpenClaw 代理记忆备份与恢复工具，支持跨设备迁移 | ✓ |
| batch_landing | 回国、数据回国、批量回国 | 批量数据回国 | ✓ |
| calculator | 计算、算术、加减乘除、平均数、calculator | 基础计算器模块 | ✓ |
| create | 创建、新建、模块生成、gtools create | 创建新 gtools 模块（带 SKILL.md 模板） | ✓ |
| remove | 删除、移除、模块删除、gtools remove | 删除 gtools 模块 | ✓ |
| format | 格式化、format | 通用格式化模块 | ✓ |
| test_module | 测试、test、调试 | 测试模块 | ✓ |
| update | 更新、upgrade | 更新模块 | ✓ |
| mark_imgs | 标记、图片、img、标注 | 图片标记 | ✓ |

---

## AI 路由流程

1. **读取本文档** → 提取用户请求关键词
2. **匹配模块** → 在表格中找到最相关的模块名
3. **检查 skill.md** → 执行 `gtools info <module>` 查看是否有 skill.md
4. **执行模块** → 有 skill 则阅读后执行，无 skill 则默认执行或询问参数

---

## 更新规则

- 新增模块时，在表格中添加一行
- 如果模块创建了 SKILL.md，将 skill.md 列改为 ✓
- 关键词用顿号分隔，包含中文和英文
- 描述简洁明了，突出核心功能

---

## 使用说明

### 有 skill.md 的模块
```
用户请求 → 匹配关键词 → gtools info <module> → 阅读 SKILL.md → 执行
```

### 无 skill.md 的模块
```
用户请求 → 匹配关键词 → gtools <module> -h → 使用默认方式执行或询问参数
```
