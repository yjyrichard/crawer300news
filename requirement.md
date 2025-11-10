# 网易新闻爬虫项目需求文档

## 1. 项目概述
爬取网易新闻网站的三个分类新闻，用于文本挖掘和聚类分析。

## 2. 目标网站
- **网站名称**: 网易新闻
- **目标分类**:
  1. 体育新闻: https://sports.163.com/
  2. 科技新闻: https://tech.163.com/
  3. 文化新闻: https://culture.163.com/

## 3. 数据需求

### 3.1 数据量
- 每个分类: **300篇新闻**
- 总计: **900篇新闻**

### 3.2 数据字段
每篇新闻需要提取以下信息：
- **新闻标题** (title)
- **新闻正文内容** (content) - 纯文本，不包含图片
- **发布时间** (publish_time)
- **新闻来源** (source)
- **新闻URL** (url)
- **新闻分类** (category): 体育/科技/文化

### 3.3 数据存储（双格式）
#### 格式1: CSV文件（用于批量分析）
- **文件命名**:
  - `sports_news.csv` - 体育新闻
  - `tech_news.csv` - 科技新闻
  - `culture_news.csv` - 文化新闻
  - `all_news.csv` - 合并所有新闻
- **编码**: UTF-8-BOM（支持Excel直接打开）
- **用途**: 便于机器学习和聚类分析

#### 格式2: TXT文件（用于单独查看）
- **目录结构**:
  ```
  data/txt/
  ├── sports/
  │   ├── 001_新闻标题.txt
  │   ├── 002_新闻标题.txt
  │   └── ...（300个文件）
  ├── tech/
  │   ├── 001_新闻标题.txt
  │   └── ...（300个文件）
  └── culture/
      ├── 001_新闻标题.txt
      └── ...（300个文件）
  ```
- **文件内容格式**:
  ```
  标题: 新闻标题
  分类: 体育
  时间: 2025-10-27 10:30
  来源: 新华社
  链接: https://sports.163.com/xxx

  ----------正文----------

  新闻正文内容...
  ```
- **用途**: 便于人工阅读和检查

## 4. 技术方案

### 4.1 开发语言
- Python 3.7+

### 4.2 主要依赖库
```
requests         # HTTP请求
beautifulsoup4   # HTML解析
pandas           # 数据处理和CSV导出
lxml             # XML/HTML解析器
tqdm             # 进度条显示
```

### 4.3 爬虫策略
- **请求间隔**: 1-3秒随机延迟，避免被封
- **User-Agent**: 模拟浏览器请求
- **重试机制**: 请求失败自动重试3次
- **超时设置**: 10秒超时

### 4.4 数据质量控制
- 去重：根据URL去重，避免重复爬取
- 内容过滤：过滤内容过短的新闻（< 100字）
- 错误处理：记录失败的URL到日志文件

## 5. 功能特性

### 5.1 核心功能
- [x] 自动爬取三个分类的新闻列表页
- [x] 提取每篇新闻的详情页内容
- [x] 自动清洗文本（去除HTML标签、广告等）
- [x] 同时保存为CSV和TXT两种格式

### 5.2 辅助功能
- [x] 进度显示：实时显示爬取进度（使用tqdm）
- [x] 断点续爬：支持中断后继续爬取
- [x] 日志记录：记录爬取过程和错误信息
- [x] 数据统计：显示每个分类的爬取数量

## 6. 输出示例

### 6.1 CSV文件结构
```csv
category,title,content,publish_time,source,url
体育,梅西率队夺冠,"新闻正文内容...",2025-10-27 10:30,新华社,https://sports.163.com/xxx
科技,AI技术突破,"新闻正文内容...",2025-10-27 09:15,网易科技,https://tech.163.com/xxx
文化,传统文化保护,"新闻正文内容...",2025-10-26 18:20,光明日报,https://culture.163.com/xxx
```

### 6.2 TXT文件示例
```
标题: 梅西率队夺冠
分类: 体育
时间: 2025-10-27 10:30
来源: 新华社
链接: https://sports.163.com/xxx

----------正文----------

在激烈的比赛中，梅西率领球队最终获得冠军...
（完整正文内容）
```

## 7. 项目结构
```
crawer300news/
├── requirement.md           # 需求文档（本文件）
├── crawler.py              # 主爬虫程序
├── config.py               # 配置文件
├── requirements.txt        # Python依赖
├── data/                   # 数据存储目录
│   ├── csv/               # CSV格式
│   │   ├── sports_news.csv
│   │   ├── tech_news.csv
│   │   ├── culture_news.csv
│   │   └── all_news.csv
│   └── txt/               # TXT格式
│       ├── sports/        # 300个txt文件
│       ├── tech/          # 300个txt文件
│       └── culture/       # 300个txt文件
├── logs/                   # 日志目录
│   └── crawler.log
└── README.md              # 项目说明
```

## 8. 使用流程
1. 安装依赖: `pip install -r requirements.txt`
2. 运行爬虫: `python crawler.py`
3. 查看结果:
   - CSV文件在 `data/csv/` 目录
   - TXT文件在 `data/txt/` 目录

## 9. 注意事项
- 遵守网站robots.txt协议
- 控制爬取速度，避免对服务器造成压力
- 仅用于学习和研究目的
- 爬取的数据不得用于商业用途

## 10. 预计完成时间
- 单个分类300篇，按每秒1-3篇的速度
- 预计总耗时: **15-30分钟**
- 同时生成CSV和TXT，时间基本不变

## 11. 数据使用建议

### 用CSV做聚类分析：
```python
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# 读取CSV
df = pd.read_csv('data/csv/all_news.csv')

# TF-IDF特征提取
vectorizer = TfidfVectorizer(max_features=1000)
X = vectorizer.fit_transform(df['content'])

# K-means聚类
kmeans = KMeans(n_clusters=3)
df['cluster'] = kmeans.fit_predict(X)
```

### 用TXT查看原文：
- 直接打开txt文件阅读
- 用于检查爬取质量
- 便于人工标注和分析

---

**文档版本**: v2.0
**创建日期**: 2025-10-27
**更新内容**:
- 旅游改为文化分类
- 增加TXT格式存储
- 增加数据使用示例
**用途**: 文本挖掘和聚类分析
