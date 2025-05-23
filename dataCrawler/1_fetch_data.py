import copy
import time
import secrets
import traceback
import requests
import io 
from bs4 import BeautifulSoup as bs
import json
from parse_fetched_data import Parse
from utils.connectDB import *
from utils.kafkaTools import produce_kafka_data
from utils.models import get_active_forums_query
import random
from utils.general import * 
from utils.redisTools import *

kafka_producer = connect_kafka_producer()
kafka_parsed_topics_topic = "parsed_topics"
forums = [{"forum_name" : "chip"}]
redis_db_number = 0

def forum_chip(forum_name):
    forum_data = open_file("utils/chip_forum.json", "r")
    for data in forum_data: 
        category_name = data.get("name")
        category_link = data.get("link")
        subcategories = data.get("subforums")
        subcategories = [data] if not subcategories else subcategories
        if subcategories:
            for subcategory in subcategories:
                try:
                    subcategory_name = subcategory.get("name")
                    subcategory_link = subcategory.get("link") 
                    response = requests.get(subcategory_link)
                    print(f'Sended GET Request to {subcategory_link}')
                    html_content = response.text
                    soup_list = []
                    soup = bs(html_content, "html.parser")
                    soup_list.append(soup)
                    pagination = soup.find("ul", class_="pagination")
                    if not pagination:
                        print(f"Pagination not found in {subcategory_link}")
                        continue
                    page_links = pagination.find_all("a")
                    page_numbers = []
                    for link in page_links:
                        try:
                            num = int(link.text.strip().replace("…", ""))  
                            page_numbers.append(num)
                        except ValueError:
                            continue
                    total_pages = max(page_numbers) if page_numbers else 1
                    if total_pages:
                        for total in range(0, total_pages):
                            try:
                                total = total if total != 0 else ''
                                subcategory_link_total = subcategory_link+str(total)+"/?sortby=lastpost&sort=asc"
                                pagination_request = requests.get(subcategory_link_total)
                                print(f'Sended GET Request to {subcategory_link+str(total)}')
                                pagination_content = pagination_request.text
                                soup = bs(pagination_content, "html.parser")
                                parsed_topics_data = Parse.get_parsed_topics_data(forum_name, soup)
                                for parsed in parsed_topics_data:
                                    subcategory_topic_link = parsed.get("subcategoryTopicData").get("link")
                                    redis_key_status = check_redis_key(subcategory_topic_link, redis_db_number)
                                    if redis_key_status is False:
                                        parsed['categoryData'] = {
                                                'name' : category_name,
                                                'link' : category_link,
                                                'description' : data.get('description')
                                                }
                                        parsed['subcategoryData'] = {
                                                'name' : subcategory_name,
                                                'link' : subcategory_link
                                                }
                                        parsed['platformData'] = {
                                                'name' : 'chip',
                                                'link' : 'https://www.chip.com.tr/',
                                                'forumLink' : 'https://forum.chip.com.tr/forum/'
                                                }
                                        produce_kafka_data(kafka_producer, kafka_parsed_topics_topic, json.dumps(parsed))
                                        status = set_redis_key(subcategory_topic_link, redis_db_number)
                                        print(f'Data sended to Kafka succesfully. {subcategory_link_total}')
                            except:
                                continue
                        kafka_producer.flush()
                except:
                    traceback.print_exc()
                    continue
                
def create_app():
    active_forums = PsqlQuery.get_active_forums_query()
    for forum in forums:
        forum_name = forum.get("forum_name")
        if forum_name == "chip":
            forum_chip(forum_name)    

create_app()


