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

from parse_fetched_data import Parse
from utils.connectDB import *
from utils.kafkaTools import produce_kafka_data
from utils.models import PsqlQuery
from utils.general import open_file
from utils.redisTools import *

#kafka_producer = connect_kafka_producer()
kafka_parsed_categories_topic = "parsed_categories"
redis_db_number = 0

async def send_get_requests(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.text()
            return data

async def run_bot(bot_id, platform, url):
    print(platform, url)
    #response = await send_get_requests(url)

async def create_app():
    while True:
        active_platforms = PsqlQuery.get_active_forums_query()
        bot_count = len(active_platforms) * 2
        bot_tasks = []
        for bot_index in range(bot_count):
            if bot_index < len(active_platforms):
                assigned_platform_name = active_platforms[bot_index][0]
                platform_request_url = active_platforms[bot_index][1]
            else:
                assigned_platform_name = active_platforms[bot_index % len(active_platforms)][0]
                platform_request_url = active_platforms[bot_index % len(active_platforms)][1]
            bot_task = asyncio.create_task(run_bot(bot_id=bot_index + 1, platform=assigned_platform_name))
            bot_tasks.append(bot_task)
        await asyncio.gather(*bot_tasks)

if __name__ == "__main__":
    asyncio.run(create_app())
