# 英雄详细设计文档 (Hero Design Specification)

游戏基础数据基于 LoL 15.24.1 版本

为了确保你的 AstrBot 插件能获取到最新的《英雄联盟》数据，这里给出具体的 URL 和调用逻辑。

## 1. 核心数据接口 (具体 URL)

目前的 DDragon 版本（截至 2025 年末）通常在 15.x.x 左右。你可以通过以下步骤动态获取或直接使用示例 URL。

### A. 获取最新版本号 (Best Practice)

在请求具体数据前，建议先访问这个接口获取当前的 [版本号]，以保证数据不过期。

- **URL**: https://ddragon.leagueoflegends.com/api/versions.json
- **返回示例**: `["15.24.1", "15.23.1", ...]` (取列表第一个即为最新)

### B. 英雄数据 JSON (以 15.24.1 为例)

> **注意**: `champion.json` 只有基础信息。如果你做游戏需要详细的技能数值（伤害、冷却、蓝耗），必须使用 `championFull.json`。

- **基础列表** (包含头像/ID/简述): https://ddragon.leagueoflegends.com/cdn/15.24.1/data/zh_CN/champion.json
- **完整数据** (包含详细技能数值): https://ddragon.leagueoflegends.com/cdn/15.24.1/data/zh_CN/championFull.json

### C. 图片资源 URL

假设你从 JSON 中解析出艾希 (Ashe) 的 Q 技能 ID 为 `AsheQ`。

- **技能图标**: https://ddragon.leagueoflegends.com/cdn/15.24.1/img/spell/AsheQ.png
- **英雄正方形头像**: https://ddragon.leagueoflegends.com/cdn/15.24.1/img/champion/Ashe.png
- **英雄加载界面长图** (Loading Screen): https://ddragon.leagueoflegends.com/cdn/img/champion/loading/Ashe_0.jpg

## 2. 开发建议：如何解析

在 `championFull.json` 中，结构如下，你需要提取 `spells` 数组中的 `id` 来拼接图片 URL：

```json
"Ashe": {
    "spells": [
        {
            "id": "AsheQ", 
            "name": "射手的专注",
            "cooldown": [10, 9, 8, 7, 6],
            "cost": [50, 50, 50, 50, 50],
            ...
        },
        ...
    ]
}
```

# 英雄数据表设计文档 (Hero Database Schema v2.0)

## 1. 基础信息 (Identity & Metadata)

用于界定英雄身份及在 UI 中的展示。

| 字段名 (Field) | 类型   | 含义     | 详细说明                                    |
| -------------- | ------ | -------- | ------------------------------------------- |
| id             | Int    | 序号/ID  | 主键。唯一标识符（例如：艾希=1）            |
| name_en        | String | 英文名称 | 资源索引键。用于调用图片（如 Ashe.png）或音频 |
| name_zh        | String | 中文名称 | 界面显示的英雄名字（如 艾希）               |
| nickname       | String | 绰号     | 英雄的荣誉称号（如 寒冰射手）               |
| sort_index         | Int    | 排序权重 | 在图鉴或选人界面的显示优先级。数值越小越靠前 |
| description    | Text   | 简介     | 英雄的背景故事描述（Flavor Text）           |

## 2. 核心战斗属性 (Core Combat Stats - Base)

英雄在 1级 时的初始状态。

| 字段名 (Field)      | 类型  | 含义         | 详细说明                                    |
| ------------------- | ----- | ------------ | ------------------------------------------- |
| resource_type             | Int   | 法力值类型   | 0=无消耗, 1=法力(Mana), 2=能量(Energy), 3=怒气/其他 |
| base_hp             | Int   | 基础血量     | 1级时的最大生命值                           |
| base_mp             | Int   | 基础法力值   | 1级时的最大资源值。若 resource_type=0 此处可忽略  |
| base_attack         | Int   | 基础攻击 (AD)| 1级时的物理攻击力                           |
| base_ap             | Int   | 基础法强 (AP)| 1级时的法术强度（通常为0）                  |
| base_armor          | Int   | 基础护甲     | 1级时的物理防御                             |
| base_mr             | Int   | 基础魔抗     | 1级时的魔法防御                             |
| base_attack_speed   | Float | 基础攻速系数 | 重要：LoL的攻速基数（如 0.658）             |

> 在回合制中，可用于计算多段攻击概率或修正伤害倍率。

| 字段名 (Field)  | 类型  | 含义         | 详细说明                                    |
| --------------- | ----- | ------------ | ------------------------------------------- |
| base_move_speed | Int   | 基础移动速度 | 核心属性：决定回合制的出手顺序 (Priority)   |
| base_hp_regen   | Float | 基础生命回复 | 每回合结束时自动恢复的 HP 数值              |
| base_mp_regen   | Float | 基础法力回复 | 每回合结束时自动恢复的 MP 数值              |
| base_crit       | Float | 基础暴击率   | 1级时的暴击概率（0-100%）。通常为 0        |

## 3. 成长属性 (Growth Stats - Per Level)

用于计算英雄升级后的属性。

**计算公式**： 当前属性 = 基础属性 + (成长值 × (当前等级 - 1))

> (注：攻速计算较为特殊，见下方备注)

| 字段名 (Field)              | 类型  | 含义         | 详细说明                                    |
| --------------------------- | ----- | ------------ | ------------------------------------------- |
| base_hp_per_level           | Int   | 生命成长     | 每升一级增加的 HP 上限                      |
| base_mp_per_level           | Int   | 法力成长     | 每升一级增加的 MP 上限                      |
| base_attack_per_level       | Int   | 攻击成长     | 每升一级增加的 AD                           |
| base_armor_per_level        | Float | 护甲成长     | 每升一级增加的 Armor                        |
| base_mr_per_level           | Float | 魔抗成长     | 每升一级增加的 MR                           |
| base_attack_speed_per_level | Float | 攻速成长(%)  | 注意：这是百分比数值（如 3.33 代表 3.33%）  |

**公式**：当前攻速 = 基础攻速 * (1 + 成长% * (等级-1))

| 字段名 (Field)             | 类型  | 含义         | 详细说明                                    |
|-------------------------| ----- | ------------ | ------------------------------------------- |
| base_hp_regen_per_level | Float | 生命回复成长 | 每升一级增加的每回合回血量                  |
| base_mp_regen_per_level | Float | 法力回复成长 | 每升一级增加的每回合回蓝量                  |
| base_crit_per_level     | Float | 暴击成长     | 每升一级增加的暴击率（通常为0）             |

## 4. 技能配置 (Skill Configuration)

关联到独立的 Skills 表。

| 字段名 (Field) | 类型 | 含义        | 详细说明                        |
| -------------- | ---- | ----------- | ------------------------------- |
| ability_id     | Int  | 被动技能ID  | 英雄固有被动技能 (Passive)      |
| skill1_id       | Int  | 技能1 ID (Q)| 基础技能位 1                    |
| skill2_id       | Int  | 技能2 ID (W)| 基础技能位 2                    |
| skill3_id       | Int  | 技能3 ID (E)| 基础技能位 3                    |
| skill4_id       | Int  | 技能4 ID (R)| 终极技能位 (Ultimate)           |

## 5. RPG 生态系统 (RPG Mechanics)

用于捕捉、养成和战斗奖励机制。

| 字段名 (Field)   | 类型 | 含义         | 详细说明                                    |
| ---------------- | ---- | ------------ | ------------------------------------------- |
| base_experience  | Int  | 击败经验值   | 击败该英雄（作为野怪/对手）时提供的基础经验  |
| gender_rate      | Int  | 性别比       | -1=无性别, 0=全雄, 1=1:1, 8=全雌 (参考宝可梦机制) |
| capture_rate     | Int  | 基础捕捉率   | 捕捉成功率基数 (0-255)。数值越大越容易捕捉  |
| growth_rate_id   | Int  | 升级速率ID   | 对应经验曲线表 (1=快, 2=中, 3=慢, 4=大器晚成) |

## 示例数据映射 (基于艾希)

根据你提供的 Row 数据，数据库中的一条记录将如下所示：

