# -*- coding: utf-8 -*-
"""
网易新闻爬虫主程序 - 测试集
支持体育、娱乐、教育三个分类
同时保存为CSV和TXT格式
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import json
import logging
import re
import os
from datetime import datetime
from tqdm import tqdm
from urllib.parse import urljoin, urlparse
import config_test as config  # 使用测试集配置

# 确保日志目录存在
os.makedirs(config.LOGS_DIR, exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WangYiNewsCrawler:
    """网易新闻爬虫"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(config.HEADERS)
        self.crawled_urls = set()  # 已爬取的URL集合
        self.news_data = {category: [] for category in config.CATEGORIES.keys()}
        self.checkpoint = self.load_checkpoint()

    def load_checkpoint(self):
        """加载断点数据"""
        if os.path.exists(config.CHECKPOINT_FILE):
            try:
                with open(config.CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.crawled_urls = set(data.get('crawled_urls', []))
                    logger.info(f"✓ 加载断点数据: 已爬取 {len(self.crawled_urls)} 条新闻")
                    return data
            except Exception as e:
                logger.warning(f"加载断点数据失败: {e}")
        return {'crawled_urls': [], 'progress': {}}

    def save_checkpoint(self):
        """保存断点数据"""
        try:
            checkpoint_data = {
                'crawled_urls': list(self.crawled_urls),
                'progress': {cat: len(data) for cat, data in self.news_data.items()},
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            with open(config.CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存断点数据失败: {e}")

    def request_with_retry(self, url, max_retries=config.MAX_RETRIES):
        """带重试的HTTP请求"""
        for attempt in range(max_retries):
            try:
                time.sleep(random.uniform(*config.REQUEST_DELAY))
                response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
                response.raise_for_status()
                response.encoding = response.apparent_encoding
                return response
            except Exception as e:
                logger.warning(f"请求失败 ({attempt + 1}/{max_retries}): {url} - {e}")
                if attempt == max_retries - 1:
                    logger.error(f"请求最终失败: {url}")
                    return None
        return None

    def extract_news_links(self, html, base_url):
        """从HTML中提取新闻链接"""
        soup = BeautifulSoup(html, 'lxml')
        links = []

        # 查找所有链接
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']

            # 判断是否为新闻链接（网易新闻链接通常包含这些特征）
            # 检查是否包含年月格式 (如 /25/ /24/ 等)
            has_date = bool(re.search(r'163\.com/\d{2}/', href))

            if has_date or any(pattern in href for pattern in [
                '/article/',
                '/news/',
                'dy.163.com',  # 网易号
            ]):
                # 转换为完整URL
                full_url = urljoin(base_url, href)

                # 过滤掉非新闻链接
                if self._is_valid_news_url(full_url) and full_url not in self.crawled_urls:
                    links.append(full_url)

        # 去重
        links = list(set(links))
        logger.info(f"从列表页提取到 {len(links)} 个新闻链接")
        return links

    def _is_valid_news_url(self, url):
        """判断是否为有效的新闻URL"""
        # 排除非新闻页面
        exclude_patterns = [
            'javascript:', 'mailto:', '#',
            '/special/', '/ent/photoview/', '/photo/',
            'v.163.com', 'live.163.com', 'video.163.com',
            'comment', 'share', 'download'
        ]

        for pattern in exclude_patterns:
            if pattern in url.lower():
                return False

        # 必须包含163.com
        if '163.com' not in url:
            return False

        return True

    def parse_news_detail(self, url):
        """解析新闻详情页"""
        response = self.request_with_retry(url)
        if not response:
            return None

        try:
            soup = BeautifulSoup(response.text, 'lxml')

            # 提取标题（多种可能的HTML结构）
            title = None
            for selector in ['h1', '.post_title', '.article-title', 'title']:
                title_tag = soup.select_one(selector)
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    # 清理标题中的网站后缀
                    title = re.sub(r'_.*?网易.*?$', '', title)
                    break

            if not title:
                logger.warning(f"未找到标题: {url}")
                return None

            # 提取正文内容（多种可能的HTML结构）
            content = ""
            content_selectors = [
                '.post_body',  # 网易新闻常用
                '.post_text',
                '#endText',  # 网易新闻详情页
                '.article-body',
                'article',
                '.content'
            ]

            for selector in content_selectors:
                content_div = soup.select_one(selector)
                if content_div:
                    # 移除script、style等标签
                    for tag in content_div.find_all(['script', 'style', 'iframe']):
                        tag.decompose()

                    # 提取所有段落
                    paragraphs = content_div.find_all(['p', 'div'])
                    content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                    break

            # 如果还是没找到，尝试提取所有p标签
            if not content:
                paragraphs = soup.find_all('p')
                content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])

            # 清理内容
            content = re.sub(r'\s+', ' ', content).strip()
            content = re.sub(r'\n+', '\n', content)

            # 检查内容长度
            if len(content) < config.MIN_CONTENT_LENGTH:
                logger.warning(f"内容过短 ({len(content)}字): {url}")
                return None

            # 提取发布时间
            publish_time = ""
            time_selectors = [
                '.post_time_source',
                '.post_info',
                'time',
                '.article-time'
            ]
            for selector in time_selectors:
                time_tag = soup.select_one(selector)
                if time_tag:
                    publish_time = time_tag.get_text(strip=True)
                    # 提取时间部分
                    time_match = re.search(r'\d{4}[-/]\d{2}[-/]\d{2}[\s]\d{2}:\d{2}(:\d{2})?', publish_time)
                    if time_match:
                        publish_time = time_match.group()
                    break

            # 提取来源
            source = "网易新闻"
            source_selectors = [
                '.post_time_source',
                '.source',
                '.article-source'
            ]
            for selector in source_selectors:
                source_tag = soup.select_one(selector)
                if source_tag:
                    source_text = source_tag.get_text(strip=True)
                    # 尝试提取"来源："后面的内容
                    source_match = re.search(r'来源[：:](.*?)(\s|$)', source_text)
                    if source_match:
                        source = source_match.group(1).strip()
                    break

            news_item = {
                'title': title,
                'content': content,
                'publish_time': publish_time,
                'source': source,
                'url': url,
                'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            logger.info(f"✓ 成功解析: {title[:30]}...")
            return news_item

        except Exception as e:
            logger.error(f"解析失败: {url} - {e}")
            return None

    def crawl_category(self, category, target_urls):
        """爬取指定分类的新闻"""
        logger.info(f"\n{'=' * 50}")
        logger.info(f"开始爬取【{category}】新闻")

        # 如果target_urls是字符串，转换为列表
        if isinstance(target_urls, str):
            target_urls = [target_urls]

        logger.info(f"目标URL数量: {len(target_urls)}")
        logger.info(f"{'=' * 50}\n")

        # 检查已爬取数量
        existing_count = len(self.news_data[category])
        if existing_count >= config.TARGET_COUNT:
            logger.info(f"【{category}】已达到目标数量 ({existing_count}/{config.TARGET_COUNT})，跳过")
            return

        # 收集所有链接
        all_news_links = []
        for idx, target_url in enumerate(target_urls, 1):
            logger.info(f"正在从第{idx}个列表页提取链接: {target_url}")
            response = self.request_with_retry(target_url)
            if not response:
                logger.error(f"无法访问列表页: {target_url}")
                continue

            news_links = self.extract_news_links(response.text, target_url)
            all_news_links.extend(news_links)

            # 如果已经收集到足够的链接，可以提前结束
            if len(all_news_links) >= config.TARGET_COUNT * 2:
                logger.info(f"已收集足够链接 ({len(all_news_links)})，停止提取")
                break

        # 去重
        all_news_links = list(set(all_news_links))
        logger.info(f"总共收集到 {len(all_news_links)} 个唯一的新闻链接")

        # 进度条
        pbar = tqdm(total=config.TARGET_COUNT, desc=f"爬取{category}新闻", initial=existing_count)

        # 爬取新闻详情
        for link in all_news_links:
            if len(self.news_data[category]) >= config.TARGET_COUNT:
                break

            if link in self.crawled_urls:
                continue

            news_item = self.parse_news_detail(link)
            if news_item:
                news_item['category'] = category
                self.news_data[category].append(news_item)
                self.crawled_urls.add(link)

                # 更新进度条
                pbar.update(1)

                # 定期保存断点
                if len(self.news_data[category]) % 10 == 0:
                    self.save_checkpoint()
                    self.save_to_csv(category)
                    self.save_to_txt(news_item, category)

        pbar.close()

        # 如果还没达到目标，尝试从其他列表页爬取
        if len(self.news_data[category]) < config.TARGET_COUNT:
            logger.warning(f"【{category}】当前数量 {len(self.news_data[category])}，未达到目标 {config.TARGET_COUNT}")
            logger.info("提示：可以尝试增加列表页链接或调整爬取策略")

        logger.info(f"\n【{category}】爬取完成: {len(self.news_data[category])} 篇\n")

    def save_to_csv(self, category):
        """保存为CSV格式"""
        if not self.news_data[category]:
            return

        try:
            df = pd.DataFrame(self.news_data[category])
            csv_file = config.CSV_FILES[category]

            # 保存时使用UTF-8-BOM编码，确保Excel能正常打开
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            logger.info(f"✓ CSV保存成功: {csv_file} ({len(df)} 条)")
        except Exception as e:
            logger.error(f"CSV保存失败: {e}")

    def save_to_txt(self, news_item, category):
        """保存为TXT格式"""
        try:
            txt_dir = config.TXT_DIRS[category]
            os.makedirs(txt_dir, exist_ok=True)

            # 文件名：序号_标题.txt（去除非法字符）
            index = len([f for f in os.listdir(txt_dir) if f.endswith('.txt')]) + 1
            safe_title = re.sub(r'[\\/:*?"<>|]', '', news_item['title'][:50])
            filename = f"{index:03d}_{safe_title}.txt"
            filepath = os.path.join(txt_dir, filename)

            # 写入内容
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"标题: {news_item['title']}\n")
                f.write(f"分类: {category}\n")
                f.write(f"时间: {news_item['publish_time']}\n")
                f.write(f"来源: {news_item['source']}\n")
                f.write(f"链接: {news_item['url']}\n")
                f.write(f"\n{'=' * 50}\n正文\n{'=' * 50}\n\n")
                f.write(news_item['content'])

        except Exception as e:
            logger.error(f"TXT保存失败: {e}")

    def save_all_to_csv(self):
        """合并所有分类并保存"""
        all_news = []
        for category, news_list in self.news_data.items():
            all_news.extend(news_list)

        if all_news:
            df = pd.DataFrame(all_news)
            df.to_csv(config.CSV_FILES['all'], index=False, encoding='utf-8-sig')
            logger.info(f"✓ 合并CSV保存成功: {config.CSV_FILES['all']} ({len(df)} 条)")

    def print_statistics(self):
        """打印统计信息"""
        print("\n" + "=" * 60)
        print("测试集爬取统计信息".center(56))
        print("=" * 60)

        total = 0
        for category, news_list in self.news_data.items():
            count = len(news_list)
            total += count
            status = "✓" if count >= config.TARGET_COUNT else "✗"
            print(f"  {status} 【{category}】: {count}/{config.TARGET_COUNT} 篇")

        print("-" * 60)
        print(f"  总计: {total}/{config.TARGET_COUNT * len(config.CATEGORIES)} 篇")
        print("=" * 60)

        print("\n数据文件位置:")
        print(f"  CSV: {config.CSV_DIR}")
        print(f"  TXT: {config.TXT_DIR}")
        print(f"  日志: {config.LOG_FILE}\n")

    def run(self):
        """运行爬虫"""
        print("\n" + "=" * 60)
        print("网易新闻爬虫启动 - 测试集".center(56))
        print("=" * 60)
        print(f"  目标: 每个分类爬取 {config.TARGET_COUNT} 篇新闻")
        print(f"  分类: {', '.join(config.CATEGORIES.keys())}")
        print(f"  格式: CSV + TXT")
        print("=" * 60 + "\n")

        # 初始化目录
        config.init_directories()

        # 逐个爬取分类
        for category, url in config.CATEGORIES.items():
            try:
                self.crawl_category(category, url)
            except KeyboardInterrupt:
                logger.warning("\n用户中断爬取，正在保存数据...")
                break
            except Exception as e:
                logger.error(f"爬取【{category}】时发生错误: {e}")
                continue

        # 保存所有数据
        logger.info("\n正在保存数据...")
        for category in config.CATEGORIES.keys():
            self.save_to_csv(category)
        self.save_all_to_csv()
        self.save_checkpoint()

        # 打印统计信息
        self.print_statistics()

        logger.info("✓ 测试集爬虫运行完成！")


def main():
    """主函数"""
    try:
        crawler = WangYiNewsCrawler()
        crawler.run()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        logger.error(f"程序异常: {e}", exc_info=True)


if __name__ == '__main__':
    main()
