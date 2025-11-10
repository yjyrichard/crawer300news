# -*- coding: utf-8 -*-
"""
网易新闻爬虫配置文件
"""

import os

# 项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 目标网站配置 - 每个分类可以配置多个列表页URL
CATEGORIES = {
    # '体育': [  # 已完成300条，注释掉
    #     'https://sports.163.com/',
    # ],
    '娱乐': [
        'https://ent.163.com/',
    ],
    '教育': [
        'https://edu.163.com/',
    ]
}

# 爬取配置
TARGET_COUNT = 300  # 每个分类的目标数量
MIN_CONTENT_LENGTH = 50  # 最小内容长度（字）
REQUEST_DELAY = (1, 3)  # 请求延迟范围（秒）
REQUEST_TIMEOUT = 10  # 请求超时时间（秒）
MAX_RETRIES = 3  # 最大重试次数

# 请求头配置
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}

# 数据存储路径
DATA_DIR = os.path.join(BASE_DIR, 'data')
CSV_DIR = os.path.join(DATA_DIR, 'csv')
TXT_DIR = os.path.join(DATA_DIR, 'txt')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# CSV文件路径
CSV_FILES = {
    '体育': os.path.join(CSV_DIR, 'sports_news.csv'),  # 保留，用于已有数据
    '娱乐': os.path.join(CSV_DIR, 'ent_news.csv'),
    '教育': os.path.join(CSV_DIR, 'edu_news.csv'),
    'all': os.path.join(CSV_DIR, 'all_news.csv')
}

# TXT目录路径
TXT_DIRS = {
    '体育': os.path.join(TXT_DIR, 'sports'),  # 保留，用于已有数据
    '娱乐': os.path.join(TXT_DIR, 'ent'),
    '教育': os.path.join(TXT_DIR, 'edu')
}

# 日志文件路径
LOG_FILE = os.path.join(LOGS_DIR, 'crawler.log')

# 断点续爬配置
CHECKPOINT_FILE = os.path.join(DATA_DIR, 'checkpoint.json')

# 创建必要的目录
def init_directories():
    """初始化所有必要的目录"""
    directories = [
        DATA_DIR,
        CSV_DIR,
        TXT_DIR,
        LOGS_DIR,
    ] + list(TXT_DIRS.values())

    for directory in directories:
        os.makedirs(directory, exist_ok=True)

    print(f"✓ 目录初始化完成")
    print(f"  - CSV目录: {CSV_DIR}")
    print(f"  - TXT目录: {TXT_DIR}")
    print(f"  - 日志目录: {LOGS_DIR}")

if __name__ == '__main__':
    init_directories()
