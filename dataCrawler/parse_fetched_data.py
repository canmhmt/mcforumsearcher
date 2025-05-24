import requests
import io 
from bs4 import BeautifulSoup as bs
import json
from utils.general import * 

class Parse():
    def get_parsed_topics_data(platform, soup):
        if platform == "Chip Forum":
            threads = soup.find_all("div", class_="thread-row")
            thread_data = []
            for thread in threads:
                title_tag = thread.find("h3")
                author_tag = thread.find("span", class_="uyename")
                last_post_tag = thread.find("div", class_="info-cell").find("a")
                last_post_time_tag = thread.find("div", class_="info-cell").find("span", class_="time")
                reply_count_tag = thread.find("div", class_="count-cell")
                
                if title_tag and title_tag.a:
                    thread_title = title_tag.a.text.strip()
                    thread_link = title_tag.a["href"]
                else:
                    continue 
                
                thread_info = {
                    "subcategoryTopicData" :{
                    "title": thread_title,
                    "link": thread_link,
                    "author": author_tag.text.strip() if author_tag else "Bilinmiyor",
                    "last_post_date": last_post_tag.text.strip() if last_post_tag else "Bilinmiyor",
                    "last_post_time": last_post_time_tag.text.strip() if last_post_time_tag else "Bilinmiyor",
                    "replies": 0,
                    "views": 0}
                }

                if reply_count_tag:
                    counts = reply_count_tag.text.strip().split("\n")
                    replies = 0
                    views = 0
                    for count in counts:
                        if "Yanıt:" in count:
                            replies = count.replace("Yanıt:", "").replace(",", "").strip()
                        if "Hit:" in count:
                            views = count.replace("Hit:", "").replace(",", "").strip()
                    try:
                        thread_info["subcategoryTopicData"]["replies"] = int(replies)
                    except ValueError:
                        thread_info["subcategoryTopicData"]["replies"] = 0
                    try:
                        thread_info["subcategoryTopicData"]["views"] = int(views)
                    except ValueError:
                        thread_info["subcategoryTopicData"]["views"] = 0

                thread_data.append(thread_info)
            return thread_data
