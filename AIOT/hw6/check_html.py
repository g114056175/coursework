import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
url = 'https://ssr1.scrape.center/page/1'
try:
    response = requests.get(url, headers=headers, timeout=10)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    movie_item = soup.find('div', class_='item')
    if movie_item:
        print('=== 第一個電影項目的完整 HTML ===')
        print(movie_item.prettify())
        
        print('\n=== 查找所有 span ===')
        for span in movie_item.find_all('span'):
            print(f"Class: {span.get('class')}, Text: {span.text.strip()}")
except Exception as e:
    print(f"Error: {e}")
