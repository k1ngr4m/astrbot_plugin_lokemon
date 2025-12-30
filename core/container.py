import json
import os
import shutil
from typing import Dict, Any

from .infrastructure.repositories.sqlite_lokemon_repo import \
    SqliteLokemonRepository


class GameContainer:
    """
    依赖注入容器：负责管理所有游戏核心组件的生命周期和依赖关系。
    """

    def __init__(self, plugin_dir: str, config: Dict[str, Any]):
        self.plugin_dir = plugin_dir
        self.user_config = config  # 来自 AstrBot 面板的配置 (WebUI)

        # ================= 1. 统一路径管理 =================
        # 这里为了稳健，我们使用 AstrBot 标准的数据目录结构:

        # 尝试获取 env 中的数据目录，如果没设置则默认
        data_root = os.getenv("ASTRBOT_DATA_DIR", "data")
        self.plugin_data_dir = os.path.join(data_root, "plugins", "astrbot_plugin_lokemon")

        # 确保目录存在
        os.makedirs(self.plugin_data_dir, exist_ok=True)

        self.data_dir = "data"
        self.db_path = os.path.join(self.data_dir, "lokemon.db")
        self.assets_path = os.path.join(plugin_dir, "assets", "data", "v1")
        self.game_config_path = os.path.join(plugin_dir, "core", "config", "game_configs.json")

        # ================= 2. 加载静态配置 =================
        self.game_config = self._load_game_config()

        # ================= 3. 初始化 Repositories =================
        self.lokemon_repo = SqliteLokemonRepository(self.db_path)


        # 2. 初始化 Services (依赖注入逻辑)
        # self.user_service = UserService(
        #     user_repo=self.user_repo,
        # )

        self.data_dir = "data"

        self.tmp_dir = os.path.join(self.data_dir, "tmp")
        os.makedirs(self.tmp_dir, exist_ok=True)
        self._clear_tmp_directory()

    def _load_game_config(self) -> Dict[str, Any]:
        """加载内部静态配置 (如 LoL 版本号)"""
        if os.path.exists(self.game_config_path):
            try:
                with open(self.game_config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载游戏配置失败: {e}，将使用默认值")
        return {"lol_version": "15.24.1"}  # 降级默认值

    def _clear_tmp_directory(self):
        """清空临时目录中的文件"""
        if os.path.exists(self.tmp_dir):
            for filename in os.listdir(self.tmp_dir):
                file_path = os.path.join(self.tmp_dir, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)  # 删除文件或符号链接
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)  # 删除子目录及其内容
                except Exception as e:
                    # 如果删除失败，记录错误但不中断操作
                    print(f"删除临时文件 {file_path} 时出错: {e}")
