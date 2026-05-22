# 电商商品价格自动化采集与对比工具

从京东、淘宝、拼多多三大主流电商平台批量抓取商品信息，自动清洗去重、横向对比、价格排序，并生成可视化图表。

## 功能特性

- 🔍 **多平台采集** — 京东、淘宝、拼多多，支持按关键词批量抓取
- 🧹 **智能清洗** — 去重、价格归一化、按价格升序排列
- ⚖️ **横向对比** — 四维评分体系（价格/评分/销量/性价比）
- 🏆 **性价比推荐** — 最佳性价比、最低价格、最高销量、最佳评分
- 📊 **数据可视化** — 6 种图表：平台均价对比、价格分布、价格趋势、性价比散点图、销量排行
- 🖥️ **双入口** — CLI 命令行工具 + Web 演示页面
- 🔌 **可扩展架构** — 抽象爬虫基类，新增平台只需实现接口

## 快速开始

### 安装

```bash
# 方式一：一键安装
./install.sh

# 方式二：手动安装
pip install flask
```

### CLI 使用

```bash
# 基本搜索
python -m price_compare.cli 手机

# 指定平台
python -m price_compare.cli "蓝牙耳机" -p jd taobao

# 指定采集数量
python -m price_compare.cli 笔记本 -n 10

# 输出 JSON（方便程序处理）
python -m price_compare.cli 平板 --json

# 保存到文件
python -m price_compare.cli 相机 -o result.json
```

### Web 演示页面

```bash
python -m price_compare.server
```

然后打开 http://localhost:5000

- 初始化自动加载「手机」搜索的示例数据
- 输入关键词实时采集并展示对比结果
- 支持平台筛选、图表交互、商品链接跳转

## CLI 参数说明

| 参数 | 说明 |
|------|------|
| `keyword` | 搜索关键词（必需） |
| `-p, --platforms` | 指定平台，可选 `jd` `taobao` `pdd` |
| `-n, --max-items` | 每个平台最大采集数量，默认 20 |
| `-o, --output` | 输出 JSON 文件路径 |
| `--json` | 以 JSON 格式输出结果 |
| `--quiet` | 静默模式，仅输出数据 |

## 项目结构

```
price_compare/
├── __init__.py
├── __main__.py           # python -m price_compare 入口
├── cli.py                # CLI 命令行工具
├── server.py             # Flask Web 服务器
├── engine.py             # 核心引擎
├── models.py             # 数据模型 (Product)
├── cleaner.py             # 数据清洗与去重
├── comparator.py          # 横向对比与推荐
├── visualizer.py          # 图表数据生成 & 报告
└── scrapers/
    ├── base.py            # 抽象爬虫基类
    ├── jd.py              # 京东爬虫
    ├── taobao.py          # 淘宝爬虫
    └── pdd.py             # 拼多多爬虫

web/
├── index.html             # 演示网页
└── demo_data.json         # 初始化示例数据
```

## 扩展真实爬虫

当前内置模拟数据，架构预留了真实爬虫扩展点。实现步骤：

1. 在 `scrapers/` 下新建文件，如 `scrapers/jd_real.py`
2. 继承 `BaseScraper` 并实现 `search()` 和 `get_product_detail()` 方法
3. 在 `scrapers/__init__.py` 的 `SCRAPER_REGISTRY` 中注册
4. 可选集成 Selenium/Playwright 处理动态渲染

```python
from .base import BaseScraper

class JDRealScraper(BaseScraper):
    platform_name = "京东"
    base_url = "https://search.jd.com"

    def search(self, keyword: str, max_items: int = 20) -> List[Product]:
        # TODO: 实现真实爬取逻辑
        raise NotImplementedError
```

## 技术栈

- Python 3.10+
- Flask — Web 服务器
- Chart.js — 前端图表
- 纯前端 HTML/CSS/JS — 无需构建

## 声明

数据为模拟生成，仅供架构演示和研究学习使用。
