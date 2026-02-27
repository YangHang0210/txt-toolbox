"""
TXT Toolbox - 文本文件处理工具
功能：排序、去重、差集删除
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import locale


WINDOW_TITLE = "TXT 工具箱"
WINDOW_SIZE = "780x620"
PADDING = 12


def read_lines(filepath: str) -> list[str]:
    """读取文件所有行（自动检测编码），返回不含换行符的纯内容列表"""
    for encoding in ("utf-8", "utf-8-sig", "gbk", "gb2312", "latin-1"):
        try:
            with open(filepath, "r", encoding=encoding) as f:
                return [line.rstrip("\r\n") for line in f.readlines()]
        except (UnicodeDecodeError, LookupError):
            continue
    raise ValueError(f"无法识别文件编码: {filepath}")


def write_lines(filepath: str, lines: list[str]) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        if lines:
            f.write("\n")


def sort_file(filepath: str, reverse: bool = False) -> tuple[int, str]:
    """对文件内容按行排序，返回 (行数, 输出路径)"""
    lines = read_lines(filepath)
    try:
        sorted_lines = sorted(lines, key=lambda s: locale.strxfrm(s.strip()), reverse=reverse)
    except Exception:
        sorted_lines = sorted(lines, key=lambda s: s.strip().lower(), reverse=reverse)

    base, ext = os.path.splitext(filepath)
    out_path = f"{base}_sorted{ext}"
    write_lines(out_path, sorted_lines)
    return len(sorted_lines), out_path


def deduplicate_file(filepath: str, keep_order: bool = True) -> tuple[int, int, str]:
    """去重，返回 (原始行数, 去重后行数, 输出路径)"""
    lines = read_lines(filepath)
    if keep_order:
        seen: set[str] = set()
        unique: list[str] = []
        for line in lines:
            if line not in seen:
                seen.add(line)
                unique.append(line)
    else:
        unique = list(dict.fromkeys(lines))

    base, ext = os.path.splitext(filepath)
    out_path = f"{base}_dedup{ext}"
    write_lines(out_path, unique)
    return len(lines), len(unique), out_path


def subtract_files(filepath_main: str, filepath_filter: str) -> tuple[int, int, str]:
    """从 main 文件中删除存在于 filter 文件中的行，返回 (原始行数, 结果行数, 输出路径)"""
    main_lines = read_lines(filepath_main)
    filter_lines = read_lines(filepath_filter)
    filter_set = set(filter_lines)
    result = [line for line in main_lines if line not in filter_set]

    base, ext = os.path.splitext(filepath_main)
    out_path = f"{base}_subtracted{ext}"
    write_lines(out_path, result)
    return len(main_lines), len(result), out_path


class TxtToolboxApp:
    """主应用窗口"""

    FILE_TYPES = [("文本文件", "*.txt"), ("所有文件", "*.*")]

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.minsize(700, 550)
        self._configure_style()
        self._build_ui()

    def _configure_style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", padding=6, font=("Microsoft YaHei UI", 10))
        style.configure("TLabel", font=("Microsoft YaHei UI", 10))
        style.configure("TLabelframe.Label", font=("Microsoft YaHei UI", 11, "bold"))
        style.configure("Header.TLabel", font=("Microsoft YaHei UI", 16, "bold"))
        style.configure("Accent.TButton", padding=8, font=("Microsoft YaHei UI", 10, "bold"))

    def _build_ui(self) -> None:
        main_frame = ttk.Frame(self.root, padding=PADDING)
        main_frame.pack(fill=tk.BOTH, expand=True)

        header = ttk.Label(main_frame, text="TXT 工具箱", style="Header.TLabel")
        header.pack(pady=(0, 8))

        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        notebook.add(self._build_sort_tab(notebook), text="  排序  ")
        notebook.add(self._build_dedup_tab(notebook), text="  去重  ")
        notebook.add(self._build_subtract_tab(notebook), text="  差集删除  ")

        self.log_area = scrolledtext.ScrolledText(
            main_frame, height=8, font=("Consolas", 9), state=tk.DISABLED, wrap=tk.WORD
        )
        self.log_area.pack(fill=tk.BOTH, expand=True)

    def _make_file_row(self, parent: ttk.Frame, label_text: str, row: int) -> tk.StringVar:
        """创建一行 [标签 + 输入框 + 浏览按钮] 并返回 StringVar"""
        var = tk.StringVar()
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky=tk.W, pady=4)
        entry = ttk.Entry(parent, textvariable=var, width=55)
        entry.grid(row=row, column=1, sticky=tk.EW, padx=6, pady=4)
        ttk.Button(
            parent, text="浏览…", width=8,
            command=lambda: self._browse_file(var)
        ).grid(row=row, column=2, pady=4)
        parent.columnconfigure(1, weight=1)
        return var

    def _browse_file(self, var: tk.StringVar) -> None:
        path = filedialog.askopenfilename(filetypes=self.FILE_TYPES)
        if path:
            var.set(path)

    def _log(self, msg: str) -> None:
        self.log_area.configure(state=tk.NORMAL)
        self.log_area.insert(tk.END, msg + "\n")
        self.log_area.see(tk.END)
        self.log_area.configure(state=tk.DISABLED)

    # ── 排序 Tab ──────────────────────────────────────────

    def _build_sort_tab(self, parent: ttk.Notebook) -> ttk.Frame:
        frame = ttk.Frame(parent, padding=PADDING)

        desc = ttk.Label(
            frame,
            text="功能说明：对指定 TXT 文件的每一行进行排序，结果保存为新文件（原文件名_sorted.txt）。",
            wraplength=650,
        )
        desc.pack(anchor=tk.W, pady=(0, 8))

        file_frame = ttk.Frame(frame)
        file_frame.pack(fill=tk.X)
        self.sort_file_var = self._make_file_row(file_frame, "选择文件：", 0)

        opt_frame = ttk.Frame(frame)
        opt_frame.pack(anchor=tk.W, pady=6)
        self.sort_reverse_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(opt_frame, text="降序排列（Z → A）", variable=self.sort_reverse_var).pack(side=tk.LEFT)

        btn = ttk.Button(frame, text="执行排序", style="Accent.TButton", command=self._on_sort)
        btn.pack(pady=8)
        return frame

    def _on_sort(self) -> None:
        path = self.sort_file_var.get().strip()
        if not path:
            messagebox.showwarning("提示", "请先选择要排序的文件。")
            return
        if not os.path.isfile(path):
            messagebox.showerror("错误", f"文件不存在：{path}")
            return
        try:
            count, out = sort_file(path, reverse=self.sort_reverse_var.get())
            self._log(f"[排序] 完成 ✓  共 {count} 行 → {out}")
            messagebox.showinfo("完成", f"排序完成！共 {count} 行\n输出文件：{out}")
        except Exception as e:
            self._log(f"[排序] 失败 ✗  {e}")
            messagebox.showerror("错误", str(e))

    # ── 去重 Tab ──────────────────────────────────────────

    def _build_dedup_tab(self, parent: ttk.Notebook) -> ttk.Frame:
        frame = ttk.Frame(parent, padding=PADDING)

        desc = ttk.Label(
            frame,
            text="功能说明：移除指定 TXT 文件中的重复行，保留首次出现的行。结果保存为新文件（原文件名_dedup.txt）。",
            wraplength=650,
        )
        desc.pack(anchor=tk.W, pady=(0, 8))

        file_frame = ttk.Frame(frame)
        file_frame.pack(fill=tk.X)
        self.dedup_file_var = self._make_file_row(file_frame, "选择文件：", 0)

        btn = ttk.Button(frame, text="执行去重", style="Accent.TButton", command=self._on_dedup)
        btn.pack(pady=8)
        return frame

    def _on_dedup(self) -> None:
        path = self.dedup_file_var.get().strip()
        if not path:
            messagebox.showwarning("提示", "请先选择要去重的文件。")
            return
        if not os.path.isfile(path):
            messagebox.showerror("错误", f"文件不存在：{path}")
            return
        try:
            total, unique, out = deduplicate_file(path)
            removed = total - unique
            self._log(f"[去重] 完成 ✓  原始 {total} 行，去重后 {unique} 行（删除 {removed} 行）→ {out}")
            messagebox.showinfo("完成", f"去重完成！\n原始行数：{total}\n去重后：{unique}\n删除重复：{removed}\n输出文件：{out}")
        except Exception as e:
            self._log(f"[去重] 失败 ✗  {e}")
            messagebox.showerror("错误", str(e))

    # ── 差集删除 Tab ──────────────────────────────────────

    def _build_subtract_tab(self, parent: ttk.Notebook) -> ttk.Frame:
        frame = ttk.Frame(parent, padding=PADDING)

        desc = ttk.Label(
            frame,
            text=(
                "功能说明：指定两个 TXT 文件。从【主文件】中删除所有同时存在于【过滤文件】中的行。\n"
                "结果保存为新文件（主文件名_subtracted.txt）。"
            ),
            wraplength=650,
        )
        desc.pack(anchor=tk.W, pady=(0, 8))

        file_frame = ttk.Frame(frame)
        file_frame.pack(fill=tk.X)
        self.sub_main_var = self._make_file_row(file_frame, "主文件：", 0)
        self.sub_filter_var = self._make_file_row(file_frame, "过滤文件：", 1)

        btn = ttk.Button(frame, text="执行差集删除", style="Accent.TButton", command=self._on_subtract)
        btn.pack(pady=8)
        return frame

    def _on_subtract(self) -> None:
        main_path = self.sub_main_var.get().strip()
        filter_path = self.sub_filter_var.get().strip()
        if not main_path or not filter_path:
            messagebox.showwarning("提示", "请选择主文件和过滤文件。")
            return
        for p, name in [(main_path, "主文件"), (filter_path, "过滤文件")]:
            if not os.path.isfile(p):
                messagebox.showerror("错误", f"{name}不存在：{p}")
                return
        try:
            total, remaining, out = subtract_files(main_path, filter_path)
            removed = total - remaining
            self._log(f"[差集] 完成 ✓  主文件 {total} 行，删除 {removed} 行，剩余 {remaining} 行 → {out}")
            messagebox.showinfo(
                "完成",
                f"差集删除完成！\n主文件行数：{total}\n删除行数：{removed}\n剩余行数：{remaining}\n输出文件：{out}",
            )
        except Exception as e:
            self._log(f"[差集] 失败 ✗  {e}")
            messagebox.showerror("错误", str(e))


def main() -> None:
    root = tk.Tk()
    root.iconbitmap(default="") if os.name == "nt" else None
    TxtToolboxApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
