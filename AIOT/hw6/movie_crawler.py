"""
電影爬蟲腳本 - 爬取 https://ssr1.scrape.center 的電影資訊
"""
import requests
import pandas as pd
from bs4 import BeautifulSoup
import time

def scrape_movies():
    """
    爬取電影資訊，頁數從 1 到 10
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    movies = []
    base_url = "https://ssr1.scrape.center/page/{}"
    
    for page in range(1, 11):  # 爬取第 1 到 10 頁
        try:
            url = base_url.format(page)
            print(f"正在爬取第 {page} 頁: {url}")
            
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找所有電影項目
            movie_items = soup.find_all('div', class_='item')
            
            for item in movie_items:
                try:
                    # 提取電影名稱
                    name_elem = item.find('h2')
                    name = name_elem.text.strip() if name_elem else 'N/A'
                    
                    # 提取導演
                    director_elem = item.find('span', class_='director')
                    director = director_elem.text.strip() if director_elem else 'N/A'
                    
                    # 提取演員
                    actors_elem = item.find('span', class_='actors')
                    actors = actors_elem.text.strip() if actors_elem else 'N/A'
                    
                    # 提取年份
                    year_elem = item.find('span', class_='year')
                    year = year_elem.text.strip() if year_elem else 'N/A'
                    
                    # 提取分類 / 類型
                    categories_elem = item.find('span', class_='categories')
                    categories = categories_elem.text.strip() if categories_elem else 'N/A'
                    
                    # 提取評分
                    score_elem = item.find('span', class_='score')
                    score = score_elem.text.strip() if score_elem else 'N/A'
                    
                    movie_data = {
                        '電影名稱': name,
                        '導演': director,
                        '主演': actors,
                        '年份': year,
                        '類型': categories,
                        '評分': score
                    }
                    
                    movies.append(movie_data)
                    print(f"  ✓ 成功爬取: {name}")
                    
                except Exception as e:
                    print(f"  ✗ 爬取單筆電影失敗: {e}")
                    continue
            
            # 禮貌的延遲，避免對伺服器造成過大負擔
            time.sleep(1)
            
        except requests.exceptions.RequestException as e:
            print(f"第 {page} 頁爬取失敗: {e}")
            continue
    
    return pd.DataFrame(movies)

if __name__ == "__main__":
    print("開始爬取電影資訊...")
    df = scrape_movies()
    
    if not df.empty:
        print(f"\n成功爬取 {len(df)} 部電影")
        print("\n電影資訊預覽:")
        print(df.head())
    else:
        print("沒有爬取到任何電影資訊")
