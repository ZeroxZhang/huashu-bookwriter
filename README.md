# 花叔橙皮书创作 Skill（Zerox逆向工程版）

<div align="center">

**花叔风格的书籍创作框架**

基于花叔已出版的3本技术书籍和开源仓库逆向工程得出的完整创作系统

[安装](#安装) · [使用](#使用) · [依赖](#依赖安装) · [结构](#文件结构)

</div>

---

## 简介

这是一个基于花叔（alchaincyf）已出版的技术书籍（Claude Code、OpenClaw、Hermes Agent从入门到精通系列）和开源仓库，逆向工程得出的书籍创作skill。

**核心特点**：
- 3种书籍类型蓝图（从入门到精通、橙皮书、快速指南）
- 3种章节模板（概念讲解型、实战教程型、深度分析型）
- 完整的写作风格DNA
- 质量检查清单
- PDF导出支持
- 多Agent协作支持

---

## 安装

### 方式1：复制到Claude Code skills目录

```bash
cp -r huashu-bookwriter ~/.claude/skills/
```

### 方式2：克隆仓库

```bash
git clone https://github.com/your-repo/huashu-bookwriter.git
cp -r huashu-bookwriter ~/.claude/skills/
```

---

## 依赖安装

### 必需依赖

| 依赖 | 用途 | 检查命令 |
|------|------|----------|
| Python 3.8+ | 运行脚本 | `python3 --version` |
| pandoc | Markdown转PDF | `pandoc --version` |
| XeLaTeX | PDF渲染引擎 | `xelatex --version` |

### 按平台安装

#### macOS

```bash
# 安装pandoc
brew install pandoc

# 安装LaTeX（完整版，约4GB）
brew install --cask mactex

# 或者安装精简版（推荐，约100MB）
brew install --cask basictex
sudo tlmgr install collection-fontsrecommended collection-latexrecommended

# 安装中文字体
brew install --cask font-noto-sans-cjk-sc

# 安装fontconfig（用于字体检测）
brew install fontconfig
```

#### Linux (Ubuntu/Debian)

```bash
# 安装pandoc
sudo apt update
sudo apt install pandoc

# 安装LaTeX
sudo apt install texlive-xetex texlive-latex-recommended texlive-fonts-recommended

# 安装中文支持
sudo apt install texlive-lang-chinese

# 安装中文字体
sudo apt install fonts-noto-cjk

# 安装fontconfig
sudo apt install fontconfig
```

#### Linux (CentOS/RHEL)

```bash
# 安装pandoc
sudo yum install pandoc

# 安装LaTeX
sudo yum install texlive-xetex texlive-latex

# 安装中文字体
sudo yum install google-noto-sans-cjk-fonts
```

#### Windows

```powershell
# 使用winget安装
winget install --id JohnMacFarlane.Pandoc
winget install --id MiKTeX.MiKTeX

# 或手动下载
# pandoc: https://pandoc.org/installing.html
# MiKTeX: https://miktex.org/download
```

### 验证安装

```bash
# 检查所有依赖
python3 scripts/export_pdf.py --list-fonts

# 测试PDF导出
echo "# Test" > test.md
python3 scripts/export_pdf.py test.md
```

### 常见问题

**Q: PDF中文显示乱码？**
```bash
# 确保安装了中文字体
fc-list :lang=zh

# 如果没有输出，安装中文字体
# macOS: brew install --cask font-noto-sans-cjk-sc
# Linux: sudo apt install fonts-noto-cjk
```

**Q: xelatex命令找不到？**
```bash
# macOS (BasicTeX用户需要更新PATH)
eval "$(/usr/libexec/path_helper)"

# Linux
sudo apt install texlive-xetex
```

**Q: pandoc报错"pdf-engine not found"？**
```bash
# 确保xelatex在PATH中
which xelatex

# 如果没有，安装LaTeX
# macOS: brew install --cask mactex
# Linux: sudo apt install texlive-xetex
```

---

## 使用

### 触发方式

当你说以下内容时会自动触发：
- "写一本书"
- "帮我写个指南"
- "创作XX从入门到精通"
- "做个橙皮书"

### 基本流程

```
1. 选择书籍类型 → Type A/B/C
2. 确认选题 → 目标读者、信息密度
3. 设计大纲 → Part结构 + §编号章节
4. 信息搜集 → 官方文档、社区资源
5. 章节撰写 → 遵循风格DNA
6. 审校 → QC检查
7. PDF导出 → 封面、目录、内容
```

### PDF导出命令

```bash
# 基本用法
python3 scripts/export_pdf.py book.md

# 指定输出文件
python3 scripts/export_pdf.py book.md -o output.pdf

# 指定字体
python3 scripts/export_pdf.py book.md --font "SimHei"

# 详细输出
python3 scripts/export_pdf.py book.md -v

# 列出可用字体
python3 scripts/export_pdf.py --list-fonts
```

### 结构验证命令

```bash
# 验证书籍结构
python3 scripts/validate_structure.py book.md
```

### 多Agent协作

```bash
# 使用agent_scheduler.py调度多Agent
python3 scripts/agent_scheduler.py --task "写一本Claude Code入门书" --agents main,writer,editor

# 查看Agent状态
python3 scripts/agent_scheduler.py --status
```

---

## 文件结构

```
huashu-bookwriter/
├── SKILL.md                    # 主skill定义
├── README.md                   # 本文件
├── LICENSE                     # MIT许可证
├── references/
│   ├── book-blueprints.md      # 书籍类型蓝图
│   ├── chapter-templates.md    # 章节模板
│   ├── style-dna.md            # 写作风格DNA
│   ├── opening-techniques.md   # 开头技巧
│   ├── callout-patterns.md     # 特殊内容块模式
│   ├── quality-checkpoints.md  # 质量检查清单
│   ├── agent-protocol.md       # Agent协作流程
│   └── research-sources.md     # 调研来源指南
├── assets/
│   ├── templates/
│   │   ├── cover-template.md   # 封面模板
│   │   └── toc-template.md     # 目录模板
│   └── schemas/
│       └── outline-schema.json # 大纲数据结构
├── scripts/
│   ├── export_pdf.py           # PDF导出脚本
│   ├── validate_structure.py   # 结构验证脚本
│   └── agent_scheduler.py      # Agent调度脚本
└── tests/
    ├── baseline-checks.md      # 基线检查
    └── pressure-scenarios.md   # 压力测试
```

---

## 核心概念

### 书籍类型

| 类型 | 特点 | 适用场景 |
|------|------|----------|
| Type A | 10章±2，3 Part，双语标题 | 技术手册 |
| Type B | 17-35节，5+ Part，代码密集 | 深度技术文档 |
| Type C | 12-17章，概念+实战 | 快速指南 |

### 写作风格DNA

- **句长**：单句≤25字
- **人称**：第一人称高频
- **数字**：具体数字，不用模糊量词
- **禁用词**：综上所述、值得注意的是...

### 质量检查

每章12项QC + 全书10项QC，确保风格一致性。

---

## 致敬与免责声明

本 Skill 是对花叔（alchaincyf）及其优秀的“橙皮书系列”技术书籍和开源项目的致敬、感谢与深度学习之作。

作为一个学习和逆向工程的产物，如果本 Skill 在还原花叔的创作框架、风格 DNA 或方法论上存在不到位或理解偏差的地方，还请广大技术爱好者多加海涵。

**特别声明：**
本项目仅出于个人学习、研究与技术分享的目的，绝无任何侵权的意图。如原作者（花叔）认为本项目的存在或发布有任何不妥，或不同意本项目的开源分享，本人可以随时撤销发布并删除相关内容。

---

## 参考资料

### 灵感来源

- [elon-musk-skill](https://github.com/alchaincyf/elon-musk-skill) - 作者的开源skill
- [feynman-skill](https://github.com/alchaincyf/feynman-skill) - 作者的开源skill
- [hermes-agent-orange-book](https://github.com/alchaincyf/hermes-agent-orange-book) - 书籍产物

### 作者

**花叔** · AI Native Coder · 独立开发者

- 公众号：花叔
- B站：AI进化论-花生
- GitHub：alchaincyf

---

## 许可证

[MIT License](LICENSE)