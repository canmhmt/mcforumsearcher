import requests

# Hedef URL
url = "https://www.technopat.net/sosyal/konu/3500-tl-kablosuz-kulaklik-oenerisi.2491071/"

# GET isteği gönder
response = requests.get(url)

# Yanıtın HTML içeriğini al
html_content = response.text

# HTML içeriğini dosyaya kaydet
with open("chip_forum.html", "w", encoding="utf-8") as file:
    file.write(html_content)

print("HTML içeriği 'chip_forum.html' dosyasına kaydedildi.")
