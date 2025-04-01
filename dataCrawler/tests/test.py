import requests
import io 
from bs4 import BeautifulSoup as bs
import json

forums = [{"forum_name" : "chip"}]

def get_parsed_topics_data(platform, soup):
    if platform == "chip":
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
                "title": thread_title,
                "link": thread_link,
                "author": author_tag.text.strip() if author_tag else "Bilinmiyor",
                "last_post_date": last_post_tag.text.strip() if last_post_tag else "Bilinmiyor",
                "last_post_time": last_post_time_tag.text.strip() if last_post_time_tag else "Bilinmiyor",
                "replies": 0,
                "views": 0
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
                    thread_info["replies"] = int(replies)
                except ValueError:
                    thread_info["replies"] = 0
                try:
                    thread_info["views"] = int(views)
                except ValueError:
                    thread_info["views"] = 0

            thread_data.append(thread_info)
        return thread_data

def forum_chip(forum_name):
    with io.open("chip_forum.json", "r", encoding = "utf-8") as json_ref:
        forum_data = json.load(json_ref)
    for data in forum_data: 
        category_name = data.get("name")
        category_link = data.get("link")
        category_description = data.get("description")
        subcategories = data.get("subforums")
        for subcategory in subcategories:
            subcategory_name = subcategory.get("name")
            subcategory_link = subcategory.get("link") 
            response = requests.get(subcategory_link)
            html_content = response.text
            soup = bs(html_content, "html.parser")
            pagination = soup.find("ul", class_="pagination")
            if pagination:
                page_links = pagination.find_all("a")
                page_numbers = []
                for link in page_links:
                    try:
                        num = int(link.text.strip().replace("…", ""))  
                        page_numbers.append(num)
                    except ValueError:
                        continue
                total_pages = max(page_numbers) if page_numbers else 1
                if total_pages and total_pages != 1:
                    for total in range(1, total_pages):
                        pagination_request = requests.get(subcategory_link+str(total))
                        pagination_content = pagination_request.text
                        pagination_soup = bs(pagination_content, "html.parser")
                        parsed_topics_data = get_parsed_topics_data(forum_name, pagination_soup)
                        

                        

                        
def create_app():
    for forum in forums:
        forum_name = forum.get("forum_name")
        if forum_name == "chip":
            forum_chip(forum_name)    

create_app()
