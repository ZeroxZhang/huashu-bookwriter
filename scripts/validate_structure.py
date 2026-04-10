#!/usr/bin/env python3
"""
结构验证脚本
验证Markdown书籍的结构是否符合规范
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Pattern


@dataclass
class ValidationError:
    """验证错误"""
    line: int
    message: str
    severity: str  # error, warning


@dataclass
class Chapter:
    """章节信息"""
    id: str
    title: str
    line: int
    has_time_anchor: bool = False
    has_forward_bridge: bool = False


@dataclass
class ValidationResult:
    """验证结果"""
    errors: List[ValidationError] = field(default_factory=list)
    chapters: List[Chapter] = field(default_factory=list)

    def add_error(self, line: int, message: str, severity: str = "error") -> None:
        """添加验证错误"""
        self.errors.append(ValidationError(line=line, message=message, severity=severity))

    @property
    def error_count(self) -> int:
        """错误数量"""
        return len([e for e in self.errors if e.severity == "error"])

    @property
    def warning_count(self) -> int:
        """警告数量"""
        return len([e for e in self.errors if e.severity == "warning"])


class BookValidator:
    """书籍结构验证器"""

    # 禁用词列表（编译为正则，提高性能）
    FORBIDDEN_WORDS: List[str] = [
        "综上所述",
        "值得注意的是",
        "接下来我们将",
        "进行操作",
        "强大的",
        "革命性的",
    ]

    # 时间线锚点模式（预编译正则）
    TIME_ANCHOR_PATTERNS: List[Pattern] = [
        re.compile(r"用了?\s*\d+\s*(天|周|月|年)"),
        re.compile(r"\d+\s*(天|周|月|年)[以之]?前"),
        re.compile(r"去年|今年|上(个)?月|这个月"),
        re.compile(r"凌晨|昨天|前天|上周"),
        re.compile(r"\d{4}年\d{1,2}月"),  # 2026年4月
        re.compile(r"上周|本周|下周"),
    ]

    # 向前桥接模式
    FORWARD_BRIDGE_PATTERNS: List[Pattern] = [
        re.compile(r"下一章"),
        re.compile(r"接下来"),
        re.compile(r"后面[我们将要]"),
        re.compile(r"在第[一二三四五六七八九十\d]+章"),
    ]

    # 章节编号模式
    CHAPTER_PATTERN: Pattern = re.compile(r"^##\s+§(\d+)\s+(.+)$")

    def __init__(self, content: str):
        self.content = content
        self.lines = content.split("\n")
        self.result = ValidationResult()

        # 预编译禁用词正则（单次编译，多次使用）
        self._forbidden_word_pattern = re.compile(
            "|".join(re.escape(word) for word in self.FORBIDDEN_WORDS)
        )

    def validate(self) -> bool:
        """执行完整验证"""
        self.check_metadata()
        self.check_chapters()
        self.check_forbidden_words_optimized()
        self.check_structure()

        # 输出结果
        self.print_results()

        return self.result.error_count == 0

    def check_metadata(self) -> None:
        """检查元数据块"""
        required_fields: List[str] = [
            "**创建者**",
            "**为谁创建**",
            "**基于**",
            "**最后更新**",
            "**适用场景**",
        ]

        # 只检查前50行
        header_content = "\n".join(self.lines[:50])
        found_fields: Set[str] = set()

        for field in required_fields:
            if field in header_content:
                found_fields.add(field)

        missing = set(required_fields) - found_fields
        if missing:
            self.result.add_error(
                line=1,
                message=f"缺少元数据字段: {', '.join(missing)}",
                severity="error"
            )

    def check_chapters(self) -> None:
        """检查章节结构"""
        for i, line in enumerate(self.lines):
            match = self.CHAPTER_PATTERN.match(line)
            if match:
                chapter_id = f"§{match.group(1)}"
                chapter_title = match.group(2)
                self.result.chapters.append(Chapter(
                    id=chapter_id,
                    title=chapter_title,
                    line=i + 1
                ))

        # 检查章节编号连续性
        chapter_nums = [int(c.id[1:]) for c in self.result.chapters]
        expected = list(range(1, len(chapter_nums) + 1))
        if chapter_nums != expected:
            self.result.add_error(
                line=1,
                message=f"章节编号不连续: 期望 {expected}, 实际 {chapter_nums}",
                severity="error"
            )

    def check_forbidden_words_optimized(self) -> None:
        """检查禁用词（优化版本：使用单次正则扫描）"""
        for i, line in enumerate(self.lines):
            matches = self._forbidden_word_pattern.findall(line)
            for word in matches:
                self.result.add_error(
                    line=i + 1,
                    message=f"发现禁用词: '{word}'",
                    severity="warning"
                )

    def check_structure(self) -> None:
        """检查章节结构"""
        for idx, chapter in enumerate(self.result.chapters):
            start_line = chapter.line
            # 计算章节结束行
            if idx + 1 < len(self.result.chapters):
                end_line = self.result.chapters[idx + 1].line
            else:
                end_line = len(self.lines)

            chapter_content = "\n".join(self.lines[start_line:end_line])

            # 检查时间线锚点
            has_anchor = any(p.search(chapter_content) for p in self.TIME_ANCHOR_PATTERNS)
            if not has_anchor:
                self.result.add_error(
                    line=chapter.line,
                    message=f"{chapter.id}: 缺少时间线锚点开头",
                    severity="warning"
                )

            # 检查"我"的出现
            if chapter_content.count("我") < 3:
                self.result.add_error(
                    line=chapter.line,
                    message=f"{chapter.id}: '我'的出现频率不足（建议≥3次）",
                    severity="warning"
                )

            # 检查向前桥接
            has_bridge = any(p.search(chapter_content) for p in self.FORWARD_BRIDGE_PATTERNS)
            if not has_bridge:
                self.result.add_error(
                    line=chapter.line,
                    message=f"{chapter.id}: 缺少向前桥接",
                    severity="warning"
                )

    def print_results(self) -> None:
        """输出验证结果"""
        print(f"\n验证结果:")
        print(f"  ❌ 错误: {self.result.error_count}")
        print(f"  ⚠️  警告: {self.result.warning_count}")

        errors = [e for e in self.result.errors if e.severity == "error"]
        warnings = [e for e in self.result.errors if e.severity == "warning"]

        if errors:
            print("\n错误:")
            for e in errors:
                print(f"  行 {e.line}: {e.message}")

        if warnings:
            print("\n警告:")
            for e in warnings:
                print(f"  行 {e.line}: {e.message}")

        if not errors and not warnings:
            print("  ✅ 所有检查通过！")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="验证Markdown书籍结构",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s book.md              # 验证书籍结构
  %(prog)s book.md --quiet      # 静默模式，只返回退出码
        """
    )
    parser.add_argument(
        "input",
        type=Path,
        help="要验证的Markdown文件"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="静默模式，不输出详细信息"
    )

    args = parser.parse_args()

    if not args.input.exists():
        print(f"❌ 错误：文件不存在: {args.input}")
        sys.exit(1)

    content = args.input.read_text(encoding="utf-8")
    validator = BookValidator(content)
    success = validator.validate()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()