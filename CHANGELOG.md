# 更新日志 (CHANGELOG)

## [v0.0.1] - 2025-12-30

### 新增功能 (Features)
- 初始实现 Lokemon 游戏系统
- 添加核心游戏架构和依赖注入容器
- 实现数据库迁移系统和初始模式
- 创建 Lokemon 物种模型和完整属性
- 添加 SQLite 仓库实现
- 设置 AstrBot 集成的配置架构
- 实现数据设置服务用于初始游戏数据
- 添加英雄设计规范文档

### 变更说明 (Changes)
- 系统设计为英雄联盟主题的宝可梦类游戏
- 包含完整的数据库模式、仓库、服务和配置
- 使用 League of Legends 数据作为 Lokemon 的基础
- 实现了完整的数据表结构，包括基础战斗属性、成长属性和技能配置
- 集成 AstrBot 配置系统，支持 WebUI 管理

### 技术细节 (Technical Details)
- 创建了 `lokemon_species` 数据表，包含 ID、中英文名称、昵称、各种战斗属性等
- 实现了数据库迁移脚本 `001_initial_lokemon.py`
- 配置了 AstrBot 插件配置架构 (`_conf_schema.json`)
- 添加了数据设置服务用于初始化游戏数据
- 实现了 SQLite 仓库抽象和具体实现

### 文件变更
- 新增 `core/container.py`: 依赖注入容器
- 新增 `core/infrastructure/database/`: 数据库相关实现
- 新增 `core/infrastructure/repositories/`: 仓库接口和实现
- 新增 `core/models/`: Lokemon 模型定义
- 新增 `docs/Hero_Design_Specification.md`: 设计文档
- 修改 `main.py`: 集成新功能