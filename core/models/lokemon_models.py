from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LokemonSpecies:
    """
    撸可梦种族模板 (Species Template)
    对应数据库表: lokemon_species
    存储该种族的基础数值，不包含个体差异（个体差异应在 Lokemon 实例类中处理）。
    """
    # ================= 1. 基础信息 (Identity) =================
    id: int
    name_zh: str
    name_en: str
    nickname: Optional[str] = None  # 称号 (如: 寒冰射手)
    sort_index: int = 0  # 图鉴排序权重
    description: Optional[str] = None  # 简介/背景故事

    # ================= 2. 核心战斗属性 (Base Stats) =================
    # 1级时的基础属性
    resource_type: int = 0  # 0=无消耗, 1=法力, 2=能量, 3=怒气
    base_hp: int = 0  # 基础生命值
    base_mp: int = 0  # 基础资源值
    base_attack: int = 0  # 基础攻击力 (AD)
    base_ap: int = 0  # 基础法强 (AP)
    base_armor: int = 0  # 基础护甲
    base_mr: int = 0  # 基础魔抗
    base_attack_speed: float = 0.0  # 基础攻速系数 (如 0.658)
    base_move_speed: int = 0  # 基础移动速度
    base_hp_regen: float = 0.0  # 基础生命回复
    base_mp_regen: float = 0.0  # 基础资源回复
    base_crit: float = 0.0  # 基础暴击率

    # ================= 3. 成长属性 (Growth Stats) =================
    # 每升一级增加的属性值
    base_hp_per_level: int = 0
    base_mp_per_level: int = 0
    base_attack_per_level: float = 0.0  # 攻击力成长可能是小数
    base_armor_per_level: float = 0.0
    base_mr_per_level: float = 0.0
    base_attack_speed_per_level: float = 0.0  # 攻速成长(%)
    base_hp_regen_per_level: float = 0.0
    base_mp_regen_per_level: float = 0.0
    base_crit_per_level: float = 0.0

    # ================= 4. 技能配置 (Skills) =================
    # 存储技能的 ID，运行时需通过 SkillService 查找具体技能对象
    ability_id: Optional[int] = None  # 被动技能
    skill1_id: Optional[int] = None  # Q / 技能1
    skill2_id: Optional[int] = None  # W / 技能2
    skill3_id: Optional[int] = None  # E / 技能3
    skill4_id: Optional[int] = None  # R / 大招

    # ================= 5. RPG 生态机制 (Mechanics) =================
    base_experience: int = 64  # 击败提供的基础经验
    gender_rate: int = 1  # 性别比 (-1:无, 0:全雄, 1:1:1, 8:全雌)
    capture_rate: int = 45  # 基础捕捉率 (0-255)
    growth_rate_id: int = 2  # 经验曲线类型 (1:快, 2:中快, 3:慢等)

    # ================= 辅助方法 =================
    @property
    def avatar_url(self, version: str = "15.24.1") -> str:
        """
        根据英文名自动生成头像 URL (DDragon API)
        示例: https://ddragon.leagueoflegends.com/cdn/15.24.1/img/champion/Ashe.png
        """
        return f"https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{self.name_en}.png"

    def calculate_stat_at_level(self, stat_name: str, level: int) -> float:
        """
        计算特定等级的面板属性 (通用公式)
        公式: 基础 + 成长 * (等级 - 1)
        """
        if level <= 1:
            return getattr(self, f"base_{stat_name}", 0)

        base = getattr(self, f"base_{stat_name}", 0)
        growth = getattr(self, f"base_{stat_name}_per_level", 0)

        # 攻速计算较为特殊，通常是 Base * (1 + Growth% * (Lvl-1))，这里仅演示通用线性叠加
        # 如果是攻速，你需要重写逻辑
        if stat_name == "attack_speed":
            # 攻速成长通常是百分比，例如 3.3% -> 0.033
            return base * (1 + (growth / 100) * (level - 1))

        return base + growth * (level - 1)