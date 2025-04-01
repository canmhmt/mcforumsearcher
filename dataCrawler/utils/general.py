import io
import requests
import json

headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

def open_file(filename, method):
    with io.open(filename, method, encoding = 'utf-8') as file_ref:
        if filename.endswith(".json"):
            file_data = json.load(file_ref)
        else:
            file_data = file_ref.readlines()
        return file_data

def get_html_content(request_link):
    try:
        response = requests.get(request_link, headers)
        if response.status_code == 200:
            return True, response.text
        return False, None
    except:
        return False, None


