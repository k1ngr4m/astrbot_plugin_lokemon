import sqlite3
from astrbot.api import logger


def up(cursor: sqlite3.Cursor):
    """
    应用此迁移：创建项目所需的全部初始表和索引（SQLite版本）
    """
    logger.debug("正在执行 001_initial_lokemon: 创建初始表...")

    # 启用外键约束 (这个通常建议在连接建立时开启，但在这里也没问题)
    cursor.execute("PRAGMA foreign_keys = ON;")

    # --- 1. 撸可梦种族定义（图鉴） ---
    # 这是一条单独的 CREATE TABLE 语句，没问题
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS lokemon_species
                   (
                       -- 1. 基础信息 (Identity & Metadata)
                       id                          INTEGER PRIMARY KEY,    -- 序号/ID
                       name_en                     TEXT    NOT NULL,       -- 英文名称 (如 'Ashe')
                       name_zh                     TEXT    NOT NULL,       -- 中文名称 (如 '艾希')
                       nickname                    TEXT,                   -- 绰号 (如 '寒冰射手')
                       sort_index                  INTEGER,                -- 排序权重
                       description                 TEXT,                   -- 简介

                       -- 2. 核心战斗属性 (Core Combat Stats - Base)
                       resource_type               INTEGER     DEFAULT 0,  -- 法力值类型
                       base_hp                     INTEGER NOT NULL,       -- 基础血量
                       base_mp                     INTEGER     DEFAULT 0,  -- 基础法力值
                       base_attack                 INTEGER NOT NULL,       -- 基础攻击 (AD)
                       base_ap                     INTEGER     DEFAULT 0,  -- 基础法强 (AP)
                       base_armor                  INTEGER NOT NULL,       -- 基础护甲
                       base_mr                     INTEGER NOT NULL,       -- 基础魔抗
                       base_attack_speed           REAL    NOT NULL,       -- 基础攻速系数
                       base_move_speed             INTEGER NOT NULL,       -- 基础移动速度
                       base_hp_regen               REAL        DEFAULT 0,  -- 基础生命回复
                       base_mp_regen               REAL        DEFAULT 0,  -- 基础法力回复
                       base_crit                   REAL        DEFAULT 0,  -- 基础暴击率

                       -- 3. 成长属性 (Growth Stats - Per Level)
                       base_hp_per_level           INTEGER     DEFAULT 0,  -- 生命成长
                       base_mp_per_level           INTEGER     DEFAULT 0,  -- 法力成长
                       base_attack_per_level       REAL        DEFAULT 0,  -- 攻击成长
                       base_armor_per_level        REAL        DEFAULT 0,  -- 护甲成长
                       base_mr_per_level           REAL        DEFAULT 0,  -- 魔抗成长
                       base_attack_speed_per_level REAL        DEFAULT 0,-- 攻速成长(%)
                       base_hp_regen_per_level     REAL        DEFAULT 0,  -- 生命回复成长
                       base_mp_regen_per_level     REAL        DEFAULT 0,  -- 法力回复成长
                       base_crit_per_level         REAL        DEFAULT 0,  -- 暴击成长

                       -- 4. 技能配置 (Skill Configuration - Foreign Keys)
                       ability_id                  INTEGER,                -- 被动技能ID
                       skill1_id                   INTEGER,                -- 技能1 ID (Q)
                       skill2_id                   INTEGER,                -- 技能2 ID (W)
                       skill3_id                   INTEGER,                -- 技能3 ID (E)
                       skill4_id                   INTEGER,                -- 技能4 ID (R)

                       -- 5. RPG 生态系统 (RPG Mechanics)
                       base_experience             INTEGER,                -- 击败基础经验值
                       gender_rate                 INTEGER     DEFAULT 1,  -- 性别比
                       capture_rate                INTEGER     DEFAULT 45, -- 基础捕捉概率
                       growth_rate_id              INTEGER     DEFAULT 2,  -- 升级速率ID

                       is_deleted                  INTEGER     DEFAULT 0   -- 是否删除
                   );
                   """)

    # --- 2. 创建索引 (关键修复：拆分为单条执行) ---

    # 唯一索引
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_lokemon_species_name_zh ON lokemon_species(name_zh);")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_lokemon_species_name_en ON lokemon_species(name_en);")

    # 别名/称号索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_lokemon_species_nickname ON lokemon_species(nickname);")

    # 排序索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_lokemon_species_sort_index ON lokemon_species(sort_index);")

    # 外键/关联索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_lokemon_species_ability_id ON lokemon_species(ability_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_lokemon_species_growth_rate ON lokemon_species(growth_rate_id);")

    # 游戏机制索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_lokemon_species_resource_type ON lokemon_species(resource_type);")

    logger.info("✅ 001_initial_lokemon_table完成")