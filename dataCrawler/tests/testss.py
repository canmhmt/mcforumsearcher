import requests
from bs4 import BeautifulSoup
import json

# Çekmek istediğin URL
url = "https://forum.chip.com.tr/forum/counter-strike-1.3_t175631.html"

# HTTP GET isteği gönder
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}
response = requests.get(url, headers=headers)

# Eğer istek başarılıysa devam et
if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")

    # Bütün postları içeren div'leri bul
    posts = soup.find_all("div", class_="postbit_wrapper")

    data = []

    for post in posts:
        try:
            # Kullanıcı adı
            username = post.find("span", class_="uyename").text.strip()
            
            # Kullanıcının mesajı
            message = post.find("div", class_="post-text").text.strip()

            # Kullanıcının diğer bilgileri
            join_date = post.find("div", class_="pbuser user-joindate").text.strip().replace("Kayıt Tarihi:", "").replace("Kayıt:", "").strip()
            message_count = post.find("div", class_="pbuser user-posts").text.strip().split()[0]
            thanks_count = post.find("span", class_="userThanksText").text.strip().replace("Teşekkür Sayısı:", "").strip()

            # Post tarihi ve saati
            post_date = post.find("span", class_="date").text.strip()
            post_time = post.find("span", class_="time").text.strip()

            # Veriyi JSON formatına uygun bir sözlük olarak ekle
            data.append({
                "username": username,
                "join_date": join_date,
                "message_count": message_count,
                "thanks_count": thanks_count,
                "post_date": post_date,
                "post_time": post_time,
                "message": message
            })
        
        except AttributeError:
            # Eğer bir öğe eksikse, hatayı yoksay ve devam et
            continue

    # JSON dosyasına yazdır
    with open("forum_posts.json", "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    print("Veriler forum_posts.json dosyasına kaydedildi.")

else:
    print(f"Sayfa yüklenemedi, HTTP Durum Kodu: {response.status_code}")
