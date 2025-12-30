import os
import pandas as pd
from astrbot.api import logger
from ....core.infrastructure.repositories.abstract_repository import \
    AbstractLokemonRepository


class DataSetupService:
    """负责在首次启动时初始化游戏基础数据，从v1 CSV文件读取数据。"""
    def __init__(self,
                 lokemon_repo: AbstractLokemonRepository,
                 data_path: str = None
                 ):
        self.lokemon_repo = lokemon_repo

        # 如果未指定路径，则使用相对于插件根目录的路径
        if data_path is None:
            # 从当前文件路径向上五级到达插件根目录
            plugin_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            self.data_path = os.path.join(plugin_root_dir, "assets", "data", "v1")
        else:
            self.data_path = data_path

    def _read_csv_data(self, filename: str) -> pd.DataFrame:
        """读取CSV文件数据"""
        file_path = os.path.join(self.data_path, filename)
        if not os.path.exists(file_path):
            logger.warning(f"CSV文件不存在: {file_path}")
            return pd.DataFrame()
        return pd.read_csv(file_path)

    def setup_initial_data(self):
        """
        检查核心数据表是否为空，如果为空则进行数据填充。
        从v3目录中的CSV文件读取数据并填充到数据库。
        这是一个幂等操作（idempotent）。
        """
        logger.info("开始检查并初始化游戏数据...")

        try:
            # 1. 填充 撸可梦 数据
            if not self.lokemon_repo.get_all_species():
                df = self._read_csv_data("lokemon_species.csv")
                if not df.empty:
                    logger.info("正在初始化撸可梦种族数据...")

                    # 1. 处理空值：Pandas 读取空单元格为 NaN，SQLite 需要 None
                    # 使用 object 类型以支持 None 替换
                    df = df.astype(object).where(pd.notnull(df), None)

                    # 2. 核心优化：直接转为字典列表
                    # 不需要手动写 id: row['id']，自动包含 CSV 所有列
                    lokemon_data_list = df.to_dict('records')

                    self.lokemon_repo.add_species_batch(lokemon_data_list)

        except Exception as e:
            logger.error(f"初始化数据时发生全局错误: {e}")