import copy
import time
import secrets
import traceback
import requests
import io
from bs4 import BeautifulSoup as bs
import json
import threading

from parse_fetched_data import Parse
from utils.connectDB import *
from utils.kafkaTools import produce_kafka_data
from utils.models import PsqlQuery
from utils.general import open_file
from utils.redisTools import *

kafka_producer = connect_kafka_producer()
kafka_parsed_topics_topic = "parsed_topics"
redis_db_number = 0

def send_get_request(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        print(f"GET: {url}")
        return response.text
    except Exception as e:
        print(f"GET FAILED: {url} | {e}")
        return None

def get_total_pages(soup):
    pagination = soup.find("ul", class_="pagination")
    if not pagination:
        return 1
    page_links = pagination.find_all("a")
    page_numbers = []
    for link in page_links:
        try:
            num = int(link.text.strip().replace("…", ""))
            page_numbers.append(num)
        except ValueError:
            continue
    return max(page_numbers) if page_numbers else 1

def publish_topic_data(parsed, category, subcategory):
    parsed["categoryData"] = category
    parsed["subcategoryData"] = subcategory
    parsed["platformData"] = {
        'name': 'chip',
        'link': 'https://www.chip.com.tr/',
        'forumLink': 'https://forum.chip.com.tr/forum/'
    }
    produce_kafka_data(kafka_producer, kafka_parsed_topics_topic, json.dumps(parsed))

def forum_chip(forum_name):
    print("Entered forum chip")
    forum_data = open_file("utils/chip_forum.json", "r")
    for data in forum_data:
        category = {
            "name": data.get("name"),
            "link": data.get("link"),
            "description": data.get("description")
        }
        subcategories = data.get("subforums") or [data]
        for sub in subcategories:
            subcategory = {
                "name": sub.get("name"),
                "link": sub.get("link")
            }
            html = send_get_request(subcategory["link"])
            if not html:
                continue
            soup = bs(html, "html.parser")
            total_pages = get_total_pages(soup)
            for page in range(len(str(total_pages))):
                suffix = f"{page}/?sortby=lastpost&sort=desc" if page != 0 else "?sortby=lastpost&sort=desc"
                page_url = subcategory["link"] + suffix
                page_html = send_get_request(page_url)
                if not page_html:
                    continue
                try:
                    soup = bs(page_html, "html.parser")
                    parsed_data = Parse.get_parsed_topics_data(forum_name, soup)
                except Exception:
                    traceback.print_exc()
                    continue
                print(parsed_data)
                if parsed_data:
                    for parsed in parsed_data:
                        topic_link = parsed.get("subcategoryTopicData", {}).get("link")
                        if not topic_link:
                            continue
                        try:
                            if not check_redis_key(topic_link, redis_db_number):
                                publish_topic_data(parsed, category, subcategory)
                                set_redis_key(topic_link, redis_db_number)
                                print(f"Sended to Kafka : {page_url}")
                            else:
                                print("Same as Redis key", topic_link)
                        except Exception:
                            traceback.print_exc()
                            continue
            kafka_producer.flush()

def fetch_forum_data():
    while True:
        status,active_forums = PsqlQuery.get_active_forums_query()
        if status:
            for forum_name in active_forums:
                if forum_name == "chipforum":
                    forum_chip("Chip Forum")

def create_app():
    for bot in range(1,2):
        forum_bot = threading.Thread(target=fetch_forum_data)
        forum_bot.start()

if __name__ == "__main__":
    create_app()
