"""
打包脚本 - 使用 PyInstaller 将 txt_toolbox.py 打包为 Windows 单文件 exe
用法: uv run build.py
"""

import subprocess
import sys


def main() -> None:
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "TXT工具箱",
        "--clean",
        "txt_toolbox.py",
    ]
    print(f"执行命令: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print("\n打包完成！可执行文件位于 dist/ 目录下。")


if __name__ == "__main__":
    main()
