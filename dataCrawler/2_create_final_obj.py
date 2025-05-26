import requests
import traceback
import json
import time
from utils.connectDB import *
from utils.kafkaTools import *
from utils.redisTools import *
from utils.general import get_html_content
from bs4 import BeautifulSoup as bs

fetched_data_topic = "parsed_topics"
final_topic = 'parsed_final_topic'
redis_db_number = 1
consumer, producer = connect_kafka_consumer(), connect_kafka_producer()
consumer.subscribe([fetched_data_topic])

def forum_chip_final(obj_data):
    subcategory_topic_link = obj_data.get("subcategoryTopicData").get("link")
    redis_key_status = check_redis_key(subcategory_topic_link ,redis_db_number)
    if redis_key_status is False:
        status, html_content = get_html_content(subcategory_topic_link)
        print("Sended GET request to -- ", subcategory_topic_link)
        if status:
            soup = bs(html_content, "html.parser")
            posts = soup.find_all("div", class_="postbit_wrapper")
            for index, post in enumerate(posts):
                try:
                    if index == 0:
                        is_op = True
                    else:
                        is_op = False
                    username = post.find("span", class_="uyename").text.strip()
                    message = post.find("div", class_="post-text").text.strip()
                    join_date = post.find("div", class_="pbuser user-joindate").text.strip().replace("Kayıt Tarihi:", "").replace("Kayıt:", "").strip()
                    message_count = post.find("div", class_="pbuser user-posts").text.strip().split()[0]
                    thanks_count = post.find("span", class_="userThanksText").text.strip().replace("Teşekkür Sayısı:", "").strip()
                    post_date = post.find("span", class_="date").text.strip()
                    post_time = post.find("span", class_="time").text.strip()
                    topic_obj = {
                        "username": username,
                        "is_op": is_op,
                        "join_date": join_date,
                        "message_count": message_count,
                        "thanks_count": thanks_count,
                        "post_date": post_date,
                        "post_time": post_time,
                        "message": message
                    }
                    obj_data['subcategoryTopicMessageData'] = topic_obj
                    set_redis_key(subcategory_topic_link, redis_db_number)
                    produce_kafka_data(producer, final_topic, json.dumps(obj_data))
                    print("Data sended to Kafka Succesfully ", subcategory_topic_link, "\n")
                except AttributeError:
                    continue
                except:
                    traceback.print_exc()
            producer.flush()
        
def create_app():
    while True:
        status, data = consume_kafka_data(consumer) 
        if status:
            data = json.loads(data.value().decode('utf-8'))
            platform = data.get("platformData").get("name")
            if platform == 'chip':
                forum_chip_final(data)
            else:
                continue
        else:
            continue

if __name__ == '__main__':
    create_app()
