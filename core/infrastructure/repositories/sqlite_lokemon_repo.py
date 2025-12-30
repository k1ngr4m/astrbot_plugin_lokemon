import sqlite3
from typing import List, Dict, Any
from astrbot.core import logger
from .abstract_repository import AbstractLokemonRepository
from ...models.lokemon_models import LokemonSpecies


class SqliteLokemonRepository(AbstractLokemonRepository):
    """撸可梦模板仓储的SQLite实现"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        # 优化 1: 移除 threading.local，SQLite 连接开启成本极低，
        # 在 asyncio 线程池中直接使用 with connect 更安全且无状态。

    def add_species_batch(self, lokemon_data_list: List[Dict[str, Any]]) -> None:
        """
        批量添加或更新撸可梦模板 (Upsert)。
        动态构建 SQL 语句，自动适配传入字典的所有字段。
        """
        if not lokemon_data_list:
            return

        # 优化 2: 动态获取字段名
        # 假设所有字典的结构一致，取第一个字典的 key 作为列名
        keys = list(lokemon_data_list[0].keys())

        # 1. 构建列名部分: id, name_en, ...
        columns_sql = ", ".join(keys)

        # 2. 构建占位符部分: :id, :name_en, ...
        placeholders_sql = ", ".join([f":{key}" for key in keys])

        # 3. 构建更新逻辑 (Upsert): name_en=excluded.name_en, ...
        # 注意：id 是主键，不需要更新，将其排除
        update_assignments = [f"{key}=excluded.{key}" for key in keys if key != "id"]
        update_clause_sql = ", ".join(update_assignments)

        query = f"""
            INSERT INTO lokemon_species ({columns_sql})
            VALUES ({placeholders_sql})
            ON CONFLICT(id) DO UPDATE SET {update_clause_sql};
        """

        try:
            # 优化 3: 使用 Context Manager 管理连接生命周期
            # 自动处理 commit (成功时) 和 rollback (异常时)，并自动关闭连接
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.executemany(query, lokemon_data_list)
                logger.info(f"成功同步 {len(lokemon_data_list)} 条撸可梦数据到数据库。")

        except sqlite3.Error as e:
            logger.error(f"批量插入/更新数据失败: {e}")
            raise

    def get_all_species(self) -> List[LokemonSpecies]:
        """获取所有未删除的撸可梦种族模板"""
        results = []

        # 获取 dataclass 定义的所有有效字段名，用于过滤
        valid_keys = set(LokemonSpecies.__annotations__.keys())

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # 建议显式过滤已删除的数据
                cursor.execute("SELECT * FROM lokemon_species WHERE is_deleted = 0")
                rows = cursor.fetchall()

                for row in rows:
                    row_dict = dict(row)

                    # 优化 4: 健壮性过滤
                    # 仅保留 Model 中定义的字段，防止数据库字段多于代码字段导致崩溃
                    filtered_data = {k: v for k, v in row_dict.items() if k in valid_keys}

                    try:
                        template = LokemonSpecies(**filtered_data)
                        results.append(template)
                    except TypeError as e:
                        # 记录具体是哪条数据出了问题
                        logger.error(f"数据映射错误 (ID: {row_dict.get('id')}): {e}")

        except sqlite3.Error as e:
            logger.error(f"查询撸可梦数据失败: {e}")
            return []

        return results