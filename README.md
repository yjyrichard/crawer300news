# 网易新闻爬虫

自动爬取网易新闻（体育、科技、文化）三个分类的新闻，用于文本挖掘和聚类分析。

## 功能特性

* ✅ 自动爬取三个分类各300篇新闻（共900篇）

* ✅ 同时保存为CSV和TXT两种格式

* ✅ 支持断点续爬（中断后可继续）

* ✅ 实时进度显示（tqdm进度条）

* ✅ 详细日志记录

* ✅ 智能去重和内容过滤

* ✅ 友好的反爬策略（随机延迟）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行爬虫

```bash
python crawler.py
```

## 输出文件

### CSV格式（用于机器学习）

```
data/csv/
├── sports_news.csv     # 体育新闻
├── tech_news.csv       # 科技新闻
├── culture_news.csv    # 文化新闻
└── all_news.csv        # 所有新闻合并
```

**CSV字段说明：**

* `category`: 新闻分类

* `title`: 新闻标题

* `content`: 新闻正文

* `publish_time`: 发布时间

* `source`: 新闻来源

* `url`: 新闻链接

* `crawl_time`: 爬取时间

### TXT格式（用于人工阅读）

```
data/txt/
├── sports/      # 体育新闻（300个txt文件）
├── tech/        # 科技新闻（300个txt文件）
└── culture/     # 文化新闻（300个txt文件）
```

每个TXT文件格式：

```
标题: 新闻标题
分类: 体育
时间: 2025-10-27 10:30
来源: 新华社
链接: https://sports.163.com/xxx

==================================================
正文
==================================================

新闻正文内容...
```

## 配置说明

编辑 `config.py` 可修改以下配置：

```python
TARGET_COUNT = 300           # 每个分类的目标数量
MIN_CONTENT_LENGTH = 100     # 最小内容长度（字）
REQUEST_DELAY = (1, 3)       # 请求延迟范围（秒）
REQUEST_TIMEOUT = 10         # 请求超时时间（秒）
MAX_RETRIES = 3             # 最大重试次数
```

## 断点续爬

程序支持断点续爬，中断后再次运行会自动：

* 跳过已爬取的URL

* 继续爬取未完成的分类

* 断点数据保存在 `data/checkpoint.json`

## 日志文件

详细日志保存在 `logs/crawler.log`，包括：

* 爬取进度

* 成功/失败的URL

* 错误信息

* 统计数据

## 数据使用示例

### 使用pandas读取CSV

```python
import pandas as pd

# 读取所有新闻
df = pd.read_csv('data/csv/all_news.csv')

# 按分类统计
print(df['category'].value_counts())

# 查看内容长度分布
df['content_length'] = df['content'].str.len()
print(df.groupby('category')['content_length'].describe())
```

### 聚类分析示例

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import pandas as pd

# 读取数据
df = pd.read_csv('data/csv/all_news.csv')

# TF-IDF特征提取
vectorizer = TfidfVectorizer(max_features=1000)
X = vectorizer.fit_transform(df['content'])

# K-means聚类
kmeans = KMeans(n_clusters=3, random_state=42)
df['cluster'] = kmeans.fit_predict(X)

# 查看聚类结果与真实分类的对应关系
print(pd.crosstab(df['category'], df['cluster']))
```

## 注意事项

1. **遵守robots.txt协议**：程序已设置合理的请求延迟
2. **仅用于学习研究**：请勿用于商业用途
3. **网络环境**：建议在稳定的网络环境下运行
4. **预计时间**：完整爬取900篇约需15-30分钟

## 常见问题

### Q: 爬取速度慢？

A: 为避免被封，程序设置了1-3秒的随机延迟，这是正常的。

### Q: 某个分类爬不到300篇？

A: 可能是因为：

* 首页链接数量有限

* 部分链接无效或内容过短

* 可以多次运行，利用断点续爬功能

### Q: 如何清空重新爬取？

A: 删除以下文件/文件夹：

```bash
rm -rf data/
rm -rf logs/
```

## 项目结构

```
crawer300news/
├── requirement.md       # 需求文档
├── README.md           # 使用说明（本文件）
├── config.py           # 配置文件
├── crawler.py          # 主程序
├── requirements.txt    # 依赖列表
├── data/              # 数据目录
│   ├── csv/          # CSV格式
│   ├── txt/          # TXT格式
│   └── checkpoint.json  # 断点数据
└── logs/              # 日志目录
    └── crawler.log    # 运行日志
```

## 许可证

本项目仅供学习和研究使用，请遵守相关法律法规和网站服务条款。

***

**版本**: v1.0
**作者**: 杨佳宇
**日期**: 2025-10-27
