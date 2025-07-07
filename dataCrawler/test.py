import requests
from bs4 import BeautifulSoup
import re

session = requests.Session()

# 1. Ana sayfaya git → CSRF token çek
resp1 = session.get("https://forum.donanimarsivi.com/")
html = resp1.text

# CSRF token regex ile al
match = re.search(r'"csrf":"([^"]+)"', html)
if not match:
    print("CSRF token bulunamadı.")
    exit()

csrf_token = match.group(1)
print("CSRF token:", csrf_token)

# 2. Yeni mesajlar sayfasına git (CSRF token'ı header olarak gönder)
headers = {
    "User-Agent": "Mozilla/5.0",
    "X-XF-Token": csrf_token
}

resp2 = session.get("https://forum.donanimarsivi.com/whats-new/posts/", headers=headers)

# Kontrol: Hata geldi mi?
if "Güvenlik hatası" in resp2.text:
    print("Güvenlik hatası oluştu. CSRF veya cookie geçersiz.")
else:
    print("İstek başarılı.")
    # örnek: başlıkları parse et
    soup = BeautifulSoup(resp2.text, "html.parser")
    titles = soup.select(".structItem--title a")
    for t in titles:
        print(t.text.strip(), "->", "https://forum.donanimarsivi.com" + t["href"])

