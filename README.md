# Bellbird Books 库存与客户订单系统

独立书店 Bellbird Books 的库存与客户预订订单管理系统（教学项目 ISYS3001 / T19）。

采用本地命令行应用，数据以 JSON 文件持久化，无需数据库与云端部署。

## 功能范围（Sprint 1）
- 新书库存：录入、按「书名+数量」聚合管理、数量增减（到货 + / 售出 −）
- 二手书库存：每本独立实体，品相 / 采购成本 / 售价 / 来源 / 货架位置
- 客户与预订订单：录入客户、创建订单、订单状态流转
- 联合搜索（新书 + 二手书）
- 数据持久化：重启不丢失
- 自动化单元测试

详见 Confluence《数据模型设计》《业务假设清单》《项目规划书》。

## 环境要求
- Python 3.10+（本仓库以 3.14 开发/测试）
- 测试：pytest

## 快速开始
```bash
# 克隆仓库（示例地址，替换为实际）
git clone <your-repo-url> bellbird-books
cd bellbird-books

# 安装依赖（当前仅测试需要 pytest）
python -m pip install -r requirements.txt

# 运行程序
python -m src.cli

# 运行测试
python -m pytest -v
```

## 配置
配置文件 `config/config.sample.json`，首次运行会复制为 `data/db.json`。
程序无硬编码绝对路径，数据文件默认存放在 `data/` 目录。

## 目录结构
```
bellbird-books/
├── README.md
├── requirements.txt
├── config/config.sample.json   # 配置样例
├── data/                       # 运行时生成的 JSON 数据文件（不入库）
├── src/
│   ├── models.py               # 数据模型：NewBook/UsedBook/Customer/Order
│   ├── storage.py              # 本地 JSON 持久化
│   ├── inventory.py            # 库存业务逻辑（新书 ST-01/02、二手书 ST-04/06）
│   └── cli.py                  # 命令行入口
└── tests/
    └── test_inventory.py       # 新书/二手书业务规则测试（DoD 强制）
```

## Git 分支策略
- `main`：可发布主干，仅接受经过 Pull Request 评审的合并
- `feature/ST-01-new-book` 等：每个用户故事一个特性分支
- 禁止直接向 `main` 提交、禁止自行合并自己的 Pull Request

## 说明
本仓库不包含任何学生 ID 与个人隐私信息。
