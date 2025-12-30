from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from ...models.lokemon_models import LokemonSpecies

class AbstractLokemonRepository(ABC):
    """撸可梦数据仓储接口"""
    # ==========增==========
    # 添加撸可梦模板批量
    @abstractmethod
    def add_species_batch(self, lokemon_data_list: List[Dict[str, Any]]) -> None: pass

    # ==========改==========


    # ==========查==========
    # 获取所有撸可梦模板
    @abstractmethod
    def get_all_species(self) -> List[LokemonSpecies]: pass
