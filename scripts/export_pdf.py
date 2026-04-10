#!/usr/bin/env python3
"""
PDF导出脚本
使用pandoc将Markdown转换为PDF
"""

import argparse
import platform
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


# 中文字体回退列表（按优先级排序）
CHINESE_FONTS_MACOS = ["PingFang SC", "Hiragino Sans GB", "STHeiti"]
CHINESE_FONTS_LINUX = ["Noto Sans CJK SC", "WenQuanYi Micro Hei", "Droid Sans Fallback"]
CHINESE_FONTS_WINDOWS = ["Microsoft YaHei", "SimHei", "SimSun"]

# 英文等宽字体（用于代码）
MONO_FONTS = ["JetBrains Mono", "Fira Code", "Source Code Pro", "Consolas"]


def get_system() -> str:
    """获取操作系统类型"""
    return platform.system()


def get_chinese_fonts() -> List[str]:
    """根据系统返回可用的中文字体列表"""
    system = get_system()
    if system == "Darwin":
        return CHINESE_FONTS_MACOS
    elif system == "Linux":
        return CHINESE_FONTS_LINUX
    elif system == "Windows":
        return CHINESE_FONTS_WINDOWS
    else:
        return CHINESE_FONTS_LINUX  # 默认使用Linux字体


def find_available_font(fonts: List[str]) -> Optional[str]:
    """
    尝试找到系统中可用的字体

    Args:
        fonts: 字体列表

    Returns:
        第一个可用的字体名称，如果都不可用返回None
    """
    try:
        result = subprocess.run(
            ["fc-list", ":family"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            installed_fonts = result.stdout.lower()
            for font in fonts:
                if font.lower() in installed_fonts:
                    return font
    except FileNotFoundError:
        pass

    # fc-list不可用，返回第一个字体作为默认
    return fonts[0] if fonts else None


def check_pandoc() -> bool:
    """检查pandoc是否安装"""
    try:
        result = subprocess.run(
            ["pandoc", "--version"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def check_xelatex() -> bool:
    """检查xelatex是否安装"""
    try:
        result = subprocess.run(
            ["xelatex", "--version"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def check_fc_list() -> bool:
    """检查fc-list是否可用（用于字体检测）"""
    try:
        result = subprocess.run(
            ["fc-list", "--version"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def get_install_instructions() -> str:
    """返回安装指南"""
    system = get_system()
    instructions = []

    if not check_pandoc():
        if system == "Darwin":
            instructions.append("pandoc: brew install pandoc")
        elif system == "Linux":
            instructions.append("pandoc: sudo apt install pandoc")
        elif system == "Windows":
            instructions.append("pandoc: winget install --id JohnMacFarlane.Pandoc")

    if not check_xelatex():
        if system == "Darwin":
            instructions.append("xelatex: brew install --cask mactex")
        elif system == "Linux":
            instructions.append("xelatex: sudo apt install texlive-xetex texlive-lang-chinese")
        elif system == "Windows":
            instructions.append("xelatex: 从 https://miktex.org/ 下载安装")

    return "\n".join(instructions) if instructions else ""


def export_pdf(
    input_file: Path,
    output_file: Path,
    toc: bool = True,
    toc_depth: int = 2,
    font: Optional[str] = None,
    verbose: bool = False
) -> None:
    """
    将Markdown转换为PDF

    Args:
        input_file: 输入的Markdown文件路径
        output_file: 输出的PDF文件路径
        toc: 是否生成目录
        toc_depth: 目录深度
        font: 指定的中文字体，如果为None则自动检测
        verbose: 是否显示详细输出

    Raises:
        SystemExit: 转换失败时退出
    """
    # 检查依赖
    if not check_pandoc():
        print("❌ 错误：pandoc未安装。请先安装pandoc。")
        print(get_install_instructions())
        sys.exit(1)

    if not check_xelatex():
        print("⚠️  警告：xelatex未安装，PDF可能无法正确渲染中文。")
        print(get_install_instructions())

    # 确定字体
    chinese_fonts = get_chinese_fonts()
    if font:
        selected_font = font
    else:
        selected_font = find_available_font(chinese_fonts)
        if selected_font is None:
            selected_font = chinese_fonts[0]

    if verbose:
        print(f"使用字体: {selected_font}")
        print(f"系统: {get_system()}")

    # 构建pandoc命令
    cmd: List[str] = [
        "pandoc",
        str(input_file),
        "-o", str(output_file),
        "--pdf-engine=xelatex",
        "-V", f"CJKmainfont={selected_font}",
        "-V", f"mainfont={selected_font}",
        "-V", "geometry:margin=2.5cm",
        "-V", "fontsize=12pt",
        "-V", "documentclass=article",
        "--highlight-style=tango",
    ]

    if toc:
        cmd.extend(["--toc", f"--toc-depth={toc_depth}"])

    if verbose:
        print(f"命令: {' '.join(cmd)}")
    else:
        print(f"正在转换: {input_file} -> {output_file}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ PDF生成成功: {output_file}")
    else:
        print(f"❌ PDF生成失败:")
        if result.stderr:
            print(result.stderr)
        else:
            print("未知错误，请尝试使用 --verbose 查看详细信息")
        sys.exit(1)


def list_fonts() -> None:
    """列出系统可用的中文字体"""
    print("系统中文字体检测:")
    print("-" * 40)

    fonts = get_chinese_fonts()
    fc_available = check_fc_list()

    if fc_available:
        try:
            result = subprocess.run(
                ["fc-list", ":family"],
                capture_output=True,
                text=True
            )
            installed_fonts = result.stdout.lower() if result.returncode == 0 else ""
        except Exception:
            installed_fonts = ""
    else:
        installed_fonts = ""
        print("⚠️  fc-list不可用，无法精确检测字体")
        print("建议安装 fontconfig: brew install fontconfig (macOS)")

    for font in fonts:
        if font.lower() in installed_fonts:
            print(f"  ✅ {font} (已安装)")
        else:
            print(f"  ❌ {font} (未检测到)")

    print("\n建议安装:")
    system = get_system()
    if system == "Darwin":
        print("  brew install --cask font-noto-sans-cjk-sc")
    elif system == "Linux":
        print("  sudo apt install fonts-noto-cjk")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="将Markdown书籍转换为PDF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s book.md                    # 转换book.md为book.pdf
  %(prog)s book.md -o output.pdf      # 指定输出文件名
  %(prog)s book.md --font "SimHei"    # 指定字体
  %(prog)s --list-fonts               # 列出可用字体
        """
    )
    parser.add_argument(
        "input",
        type=Path,
        nargs="?",
        help="输入的Markdown文件"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="输出的PDF文件（默认：与输入同名，后缀改为.pdf）"
    )
    parser.add_argument(
        "--no-toc",
        action="store_true",
        help="不生成目录"
    )
    parser.add_argument(
        "--toc-depth",
        type=int,
        default=2,
        help="目录深度（默认：2）"
    )
    parser.add_argument(
        "--font",
        type=str,
        help="指定中文字体"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="显示详细输出"
    )
    parser.add_argument(
        "--list-fonts",
        action="store_true",
        help="列出系统可用的中文字体"
    )

    args = parser.parse_args()

    # 列出字体
    if args.list_fonts:
        list_fonts()
        return

    # 检查输入文件
    if args.input is None:
        parser.print_help()
        sys.exit(1)

    if not args.input.exists():
        print(f"❌ 错误：文件不存在: {args.input}")
        sys.exit(1)

    output = args.output or args.input.with_suffix(".pdf")

    export_pdf(
        input_file=args.input,
        output_file=output,
        toc=not args.no_toc,
        toc_depth=args.toc_depth,
        font=args.font,
        verbose=args.verbose
    )


if __name__ == "__main__":
    main()