import asyncio
import os

from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star
from astrbot.api import logger, AstrBotConfig
from .core.container import GameContainer

from .core.infrastructure.database.migration import run_migrations
from .core.services import DataSetupService


class LokemonPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.plugin_id = "astrbot_plugin_lokemon"

        # 1. 获取插件根目录
        self.plugin_dir = os.path.dirname(os.path.abspath(__file__))

        # 2. 初始化容器 (传入原始 config 即可)
        # 容器会自动处理路径计算和 game_configs.json 的加载
        self.container = GameContainer(self.plugin_dir, config)

        # 3. 从容器获取 WebUI 配置 (假设 config 结构即 _conf_schema.json)
        webui_conf = config.get("webui", {})
        self.secret_key = webui_conf.get("secret_key", "default_key")
        self.port = webui_conf.get("port", 6199)

        # 4. 兼容性 & Handler 初始化
        self._bridge_compatibility()
        self._init_handlers()

    def _init_handlers(self):
        """负责实例化所有的 Repository, Service 和 Handler"""

        # --- Handlers (注入 Plugin self) ---
        # self.user_handlers = UserHandlers(self, self.container)


    def _bridge_compatibility(self):
        """
        将容器中的 Service 映射到 self 上，以兼容现有的 Handler 代码。
        现有的 Handler 可能通过 self.plugin.user_service 调用。
        """
        # self.user_service = self.container.user_service

    async def initialize(self):
        logger.info(f"[{self.plugin_id}] 正在初始化...")

        # 1. 准备迁移路径
        migrations_path = os.path.join(self.plugin_dir, "core", "infrastructure", "database", "migrations")

        # 2. 执行数据库迁移
        try:
            await asyncio.to_thread(run_migrations, self.container.db_path, migrations_path)
        except Exception as e:
            logger.error(f"[{self.plugin_id}] 数据库迁移失败: {e}")
            return

        # 3. 初始化数据
        try:
            data_setup_service = DataSetupService(
                lokemon_repo=self.container.lokemon_repo,
                data_path=self.container.assets_path
            )
            await asyncio.to_thread(data_setup_service.setup_initial_data)
        except Exception as e:
            logger.error(f"[{self.plugin_id}] 数据初始化失败: {e}")


    # ====================== 指令注册区 ======================

    # ==========注册与初始化==========


    async def _check_port_active(self):
        """验证端口是否实际已激活"""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection("127.0.0.1", self.port),
                timeout=1
            )
            writer.close()
            return True
        except:
            return False

    async def terminate(self):
        """可选择实现异步的插件销毁方法"""
        pass