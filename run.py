# -*- coding: utf-8 -*-
import logging
import sys
import os

from links_status.all_friends import fetch_friends_data, fetch_and_process_data, deal_with_large_data
from links_status.utils.json import write_json
from links_status.utils.config import load_config
from links_status.link_status import check_links_status

# ========== 日志设置 ==========
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

# ========== 加载环境变量 ==========
# if os.getenv("GITHUB_TOKEN") is None:
#     from dotenv import load_dotenv
#     load_dotenv()

# ========== 加载配置 ==========
config = load_config("./conf.yaml")
json_url = config['spider_settings']['json_url']
friends_data = None

if config["spider_settings"]["enable"] or config["link_status"]["enable"]:
    friends_data = fetch_friends_data(json_url)
    if friends_data is None:
        logging.info("获取友情链接数据失败，程序终止")
        sys.exit(0)

# ========== 爬虫模块 ==========
if config["spider_settings"]["enable"]:
    
    logging.info("爬虫已启用")
    json_url = config['spider_settings']['json_url']
    article_count = config['spider_settings']['article_count']
    specific_rss = config['specific_RSS']

    logging.info(f"正在从 {json_url} 获取数据，每个博客获取 {article_count} 篇文章")
    fetch_result = fetch_and_process_data(
        json_url        = json_url,
        specific_RSS    = specific_rss,
        count           = article_count,
        cache_file      = "./temp/cache.json",
        friends_data    = friends_data
    )

    if fetch_result is None:
        logging.info("获取友情链接数据失败，程序终止")
        sys.exit(0)
    else:
        result, lost_friends = fetch_result

        article_count = len(result.get("article_data", []))
        logging.info(f"数据获取完毕，共 {article_count} 篇文章，正在处理数据")

        result = deal_with_large_data(result)

        write_json("./all.json", result)
        write_json("./errors.json", lost_friends)

# ========== 友链状态检测模块 ==========
if config["link_status"]["enable"]:
    logging.info("友链状态检测已启用")
    try:
        logging.info("开始检测友链状态...")
        status_result = check_links_status(config, "./status.json", friends_data=friends_data)
        logging.info(f"友链状态检测完成，可访问: {status_result['accessible_count']}, 不可访问: {status_result['inaccessible_count']}")
    except SystemExit:
        raise
    except Exception as e:
        logging.info(f"友链状态检测失败，程序终止")
        sys.exit(0)
else:
    logging.info("友链状态检测未启用")
