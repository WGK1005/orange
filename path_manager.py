"""简单的路径管理器，供 GUI 使用。

提供一个 `path_manager` 实例，包含仓库根、GUI 目录及资产目录等常用路径。
"""
from pathlib import Path


class _PathManager:
    def __init__(self):
        # 仓库根目录（本文件所在目录）
        self.repo_root = Path(__file__).resolve().parent
        # gui_app 目录（相对于仓库根）
        self.gui_dir = self.repo_root / 'gui_app'
        # 资产目录（注意项目中习惯拼写为 assest）
        self.assest_dir = self.gui_dir / 'assest'

        # 尝试创建目录以避免后续 mkdir 报错
        try:
            self.assest_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass


path_manager = _PathManager()
