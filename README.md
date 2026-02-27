# TXT 工具箱

一个轻量级的 Windows 文本文件处理工具，提供 GUI 界面，**无需安装 Python 环境**即可运行。

## 功能

| 功能 | 说明 |
|------|------|
| **排序** | 对 TXT 文件按行排序（支持升序/降序），输出 `*_sorted.txt` |
| **去重** | 移除 TXT 文件中的重复行（保留首次出现），输出 `*_dedup.txt` |
| **差集删除** | 从主文件中删除存在于过滤文件中的行，输出 `*_subtracted.txt` |

## 直接使用（Windows 用户）

从 Release 下载 `TXT工具箱.exe`，双击运行即可。

## 开发与打包

### 环境准备

```bash
cd txt-toolbox
uv venv
uv pip install -r requirements.txt
```

### 本地运行

```bash
uv run txt_toolbox.py
```

### 打包为 exe

```bash
uv run build.py
```

打包完成后，`dist/TXT工具箱.exe` 即为可分发的单文件可执行程序。

## 特性

- 自动检测文件编码（UTF-8 / GBK / GB2312）
- 处理结果保存为新文件，不会修改原始文件
- 底部日志区域记录每次操作结果
- Tab 页切换三大功能，界面简洁清晰
