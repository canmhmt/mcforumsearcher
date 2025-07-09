import copy
import time
import secrets
import traceback
import asyncio
import io
from bs4 import BeautifulSoup as bs
import json
import sys
import aiohttp
import html
import hashlib

from parse_fetched_data import Parse
from utils.connectDB import *
from utils.kafkaTools import produce_kafka_data
from utils.psqlTools import PsqlQuery
from utils.general import open_file
from utils.redisTools import *

forum_details_redis_db_number = 0
forum_details_topic = "forum_details"

async def send_get_requests(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.text()
            return data

async def parse_main_title_objects(response, platform, redis_client):
    if platform == "chipforum":
        data_obj = await parse_chip_forum(response, redis_client)
    return data_obj
    
async def parse_chip_forum(response, redis_client):
    soup = bs(response, 'html.parser')
    threads = soup.select('.thread-row')
    data = []

    for thread in threads:
        try:
            title_tag = thread.select_one('.thread-title-cell a')
            if not title_tag:
                continue

            title = title_tag.text.strip()
            url = title_tag['href'].strip()
            if url:
                status = await check_redis_key(redis_client, url)
                if status:
                    continue
            else:
                continue

            starter = thread.select_one('.smallfont .uyename').text.strip()
            start_time = thread.select_one('.smallfont .time').text.strip()

            last_post_time = thread.select_one('.info-cell .time').text.strip()
            last_post_link = thread.select_one('.info-cell a')['href'].strip()
            last_post_user = thread.select_one('.info-cell .uyename').text.strip()

            reply_view = thread.select_one('.count-cell').get_text(separator='|', strip=True).split('|')
            reply_count = int(reply_view[0].replace("Yanıt: ", "").strip())
            view_count = int(reply_view[1].replace("Hit: ", "").replace(",", "").strip())
            data.append({
                "title": title,
                "title_url": url,
                "author": starter,
                "start_time": start_time,
                "reply_count": reply_count,
                "view_count": view_count
            })
            await set_redis_key(redis_client, url)

        except Exception as e:
            traceback.print_exc()
            print(f"[!] Skipped a thread due to error: {e}")
            continue
    return data

async def check_redis_key(redis_client, data):
    hashed_data = await asyncio.to_thread(hash_data, data)
    status = await redis_client.get(hashed_data)
    return status

async def set_redis_key(redis_client, data):
    hashed_data = await asyncio.to_thread(hash_data, data)
    status = await redis_client.set(hashed_data, hashed_data)
    return status

def hash_data(data):
    hash_data = hashlib.sha256(data.encode()).hexdigest()
    return hash_data

async def run_bot(bot_id, platform, url):
    response = await send_get_requests(url)
    print(f"Successfully fetched data from {url}")
    redis_client = await connect_redis(db = forum_details_redis_db_number) 
    data = await parse_main_title_objects(response, platform, redis_client)
    print(f"Parsed fetched data from the {platform} platform.")
    producer = await connect_kafka_producer()
    try:
        if producer and data and len(data) > 0:
            await producer.start()
            await produce_kafka_data(producer, forum_details_topic, data)
        else:
            print("Data did not send to Kafka (r=empty data).")
    except Exception as e:
        print(f"Could not send data to Kafka {e}.")
    finally:
        if producer:
            await producer.stop()
        if redis_client:
            await redis_client.aclose()
        print("Producer Kafka and Redis closed, bot will sleep 5 minutes.")
        await asyncio.sleep(300)

async def create_app():
    while True:
        status, active_platforms = PsqlQuery.get_active_forums_query()
        if status and active_platforms:
            bot_count = len(active_platforms)
            bot_tasks = []
            for bot_index in range(bot_count):
                if bot_index < len(active_platforms):
                    assigned_platform_name = active_platforms[bot_index][0]
                    platform_request_url = active_platforms[bot_index][1]
                else:
                    assigned_platform_name = active_platforms[bot_index % len(active_platforms)][0]
                    platform_request_url = active_platforms[bot_index % len(active_platforms)][1]
                bot_task = asyncio.create_task(run_bot(bot_id=bot_index + 1, platform=assigned_platform_name, url=platform_request_url))
                bot_tasks.append(bot_task)
            await asyncio.gather(*bot_tasks)

if __name__ == "__main__":
    asyncio.run(create_app())
