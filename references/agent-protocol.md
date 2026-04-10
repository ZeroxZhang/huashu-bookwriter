# Agent 协作流程

多Agent协作的详细规范。定义各Agent的职责、触发时机和协作方式。

---

## Agent 角色定义

| Agent | 职责 | 触发时机 | 并行限制 |
|-------|------|----------|----------|
| 主编Agent | 大纲设计、进度协调、质量把关 | Phase 0, 2, 6, 9 | 单独执行 |
| 调研Agent | 信息搜集、事实核查 | Phase 3-4 | 最多2个并行 |
| 写作Agent | 章节撰写 | Phase 5 | 最多2个并行 |
| 编辑Agent | 审校、修复 | Phase 6 | 单独执行 |
| 排版Agent | 格式规范、PDF导出 | Phase 7-8 | 单独执行 |

---

## 完整流程

```
Phase 0: 启动（主编Agent）
    ↓ 用户确认书籍类型
Phase 1: 选题确认
    ↓ 用户确认
Phase 2: 大纲设计（主编Agent）
    ↓ 用户确认大纲
Phase 3-4: 调研（调研Agent × 2，并行）
    ↓ 结果汇总
Phase 5: 撰写（写作Agent × 2，并行）
    ↓ 每章用户确认
Phase 6: 审校（编辑Agent）
    ↓ 用户确认修复
Phase 7-8: 排版+PDF（排版Agent）
    ↓ 用户验收
Phase 9: 定稿（主编Agent）
```

---

## Phase 详细说明

### Phase 0: 启动与规划

**执行者**：主编Agent

**任务**：
1. 判断书籍类型（技术手册/方法论）
2. 创建项目目录结构
3. 初始化进度文件

**输出**：
```
book-project/
├── .book/
│   ├── progress.json
│   ├── research/
│   ├── drafts/
│   └── reviews/
├── chapters/
└── assets/
```

**交互**：向用户确认书籍类型判断

---

### Phase 1: 选题确认

**交互模式**：渐进式配置菜单

```
请选择书籍配置：

A. 主题类型
- A1 技术手册（从入门到精通）
- A2 方法论（经验总结）

B. 目标读者
- B1 初学者
- B2 有经验者
- B3 专业人士

C. 信息密度
- C1 低密度
- C2 中密度
- C3 高密度
```

**确认节点**：用户必须确认配置

---

### Phase 2: 大纲设计

**执行者**：主编Agent

**任务**：
1. 根据书籍类型选择蓝图
2. 生成分层大纲
3. 生成目录预览

**输出**：
- `.book/outline.json`
- 目录预览

**确认节点**：用户确认大纲

---

### Phase 3-4: 信息搜集与事实核查（并行）

**调研Agent #1** - 信息搜集：
- 搜集官方文档、GitHub仓库
- 整理素材库
- 提取关键信息点

**调研Agent #2** - 事实核查：
- 验证技术版本准确性
- 检查信息时效性
- 生成核查报告

**并行策略**：最多2个调研Agent同时执行

**输出**：
- `.book/research/sources.md`
- `.book/research/facts-check.md`

---

### Phase 5: 章节撰写

**执行者**：写作Agent（最多2个并行）

**每章流程**：
1. 根据章节类型选择模板
2. 撰写内容（遵循style-dna.md）
3. 执行QC检查
4. 保存草稿
5. 等待用户确认

**确认节点**：每章完成需要用户确认

**输出**：
- `.book/drafts/chapter-XX-v1.md`

---

### Phase 6: 编辑审校

**执行者**：编辑Agent

**任务**：
1. 执行每章12项QC
2. 执行全书10项QC
3. 跨章节一致性检查
4. 生成审校报告

**确认节点**：用户确认是否执行修复

**输出**：
- `.book/reviews/edit-notes.md`
- `.book/reviews/quality-report.md`

---

### Phase 7-8: 排版与PDF导出

**执行者**：排版Agent

**任务**：
1. 格式规范化
2. 生成封面
3. 生成目录
4. 合并所有章节
5. 执行PDF导出

**输出**：
- `.book/final/book-full.md`
- `.book/final/book.pdf`

**确认节点**：用户验收PDF

---

### Phase 9: 精校定稿

**执行者**：主编Agent

**任务**：
1. 最终质量检查
2. 打包交付物
3. 可选清理过程文件

**最终交付**：
```
book-project/
├── book-final.pdf
├── book-final.md
├── assets/
└── README.md
```

---

## 状态文件格式

### progress.json

```json
{
  "book_id": "xxx",
  "book_title": "...",
  "book_type": "A1",
  "target_reader": "B2",
  "density": "C2",
  "current_phase": 5,
  "phases": {
    "0": {"status": "completed", "timestamp": "..."},
    "1": {"status": "completed", "timestamp": "..."},
    "2": {"status": "completed", "timestamp": "..."},
    "3": {"status": "completed", "timestamp": "..."},
    "4": {"status": "completed", "timestamp": "..."},
    "5": {"status": "in_progress", "current_chapter": "§03"}
  },
  "chapters": [
    {
      "id": "§01",
      "status": "completed",
      "qc_result": "passed",
      "user_confirmed": true
    },
    {
      "id": "§02",
      "status": "completed",
      "qc_result": "passed",
      "user_confirmed": true
    },
    {
      "id": "§03",
      "status": "in_progress"
    }
  ]
}
```

---

## Agent 通信机制

1. **状态共享**：通过 `.book/progress.json` 共享进度
2. **文件传递**：通过 `.book/research/` 和 `.book/drafts/` 传递中间产物
3. **用户确认**：关键节点必须等待用户确认

---

## 错误处理

| 错误场景 | 处理方式 |
|---------|----------|
| 调研失败 | 重试或回退到用户手动提供素材 |
| 写作QC不通过 | 返回重写，不妥协 |
| 用户拒绝确认 | 收集反馈后重新执行 |
| PDF导出失败 | 检查pandoc配置，输出Markdown备用 |