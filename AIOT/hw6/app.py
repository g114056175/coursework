import streamlit as st
import pandas as pd
import sqlite3
import os
import subprocess
import sys
import matplotlib.pyplot as plt
import matplotlib
import requests
from bs4 import BeautifulSoup
import time

# --- 全域常數設定 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'data.db')
CRAWLER_SCRIPT = 'api_crawler.py'
TABLE_NAME = 'weather_forecast'

def run_update_script(script_name, message):
    """
    執行一個 Python 腳本來更新資料。
    - 顯示執行中的提示。
    - 成功時，在可折疊區塊中顯示日誌。
    - 失敗時，僅顯示錯誤日誌的最後幾行，避免洗版。
    """
    st.info(message)
    script_path = os.path.join(BASE_DIR, script_name)
    
    try:
        with st.spinner(f"正在執行 '{script_name}'，過程可能需要一點時間..."):
            process = subprocess.run(
                [sys.executable, script_path],
                check=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
        
        st.success(f"'{script_name}' 執行成功。")
        with st.expander("查看執行日誌"):
            st.code(process.stdout)

        if process.stderr:
            st.warning(f"'{script_name}' 執行時產生了警告訊息。")
            with st.expander("查看警告日誌"):
                st.code(process.stderr)
        return True

    except subprocess.CalledProcessError as e:
        st.error(f"執行 '{script_name}' 失敗。")
        if e.stderr:
            st.warning("錯誤摘要 (僅顯示日誌的最後部分):")
            error_lines = e.stderr.strip().split('\n')
            st.code('\n'.join(error_lines[-15:]))
        
        print(f"--- ERROR: '{script_name}' failed ---")
        print(f"Return Code: {e.returncode}")
        print(f"STDOUT:\n{e.stdout}")
        print(f"STDERR:\n{e.stderr}")
        print("--- End of Error Log ---")
        return False

    except FileNotFoundError:
        st.error(f"找不到腳本: '{script_path}'。")
        return False

def get_weather_data() -> pd.DataFrame:
    """從 data.db 資料庫讀取並處理天氣資料。"""
    if not os.path.exists(DB_FILE):
        return pd.DataFrame()
        
    try:
        conn = sqlite3.connect(DB_FILE)
        query = f"SELECT location_name, start_time, avg_temp, pop FROM {TABLE_NAME}"
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        df['start_time'] = pd.to_datetime(df['start_time'])
        df['avg_temp'] = pd.to_numeric(df['avg_temp'], errors='coerce')
        df['pop'] = pd.to_numeric(df['pop'], errors='coerce')
        
        return df.dropna()
    except Exception as e:
        st.error(f"讀取或處理資料庫 '{DB_FILE}' 時發生錯誤: {e}")
        return pd.DataFrame()

def plot_weather_chart(df, y_col, title, y_label):
    """根據指定的資料行繪製天氣趨勢圖。"""
    st.header(title)
    fig, ax = plt.subplots(figsize=(12, 6))
    
    locations = df['location_name'].unique()
    
    try:
        colors = plt.cm.get_cmap('tab10', len(locations))
    except:
        colors = plt.cm.get_cmap('viridis', len(locations))

    for i, loc in enumerate(locations):
        loc_df = df[df['location_name'] == loc].sort_values(by='start_time')
        ax.plot(loc_df['start_time'], loc_df[y_col], marker='o', linestyle='-', label=loc, color=colors(i))

    ax.set_title(title, fontsize=16)
    ax.set_xlabel('時間')
    ax.set_ylabel(y_label)
    ax.legend(title='地區', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.xticks(rotation=45, ha='right')
    fig.tight_layout(rect=[0, 0, 0.85, 1])
    st.pyplot(fig)

@st.cache_data
def scrape_movies() -> pd.DataFrame:
    """
    爬取電影資訊，頁數從 1 到 10
    提取：電影名稱、評分、類型、電影圖片 URL
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    movies = []
    base_url = "https://ssr1.scrape.center/page/{}"
    progress_placeholder = st.empty()
    
    for page in range(1, 11):
        try:
            url = base_url.format(page)
            progress_placeholder.info(f"正在爬取第 {page}/10 頁...")
            
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            movie_items = soup.find_all('div', class_='item')
            
            for item in movie_items:
                try:
                    # 電影名稱
                    name_elem = item.find('h2')
                    name = name_elem.text.strip() if name_elem else 'N/A'
                    
                    # 評分（從 p class="score" 提取）
                    score_elem = item.find('p', class_='score')
                    score = score_elem.text.strip() if score_elem else 'N/A'
                    
                    # 類型（從 categories div 中的 button 內容提取）
                    categories_buttons = item.find('div', class_='categories')
                    categories_list = []
                    if categories_buttons:
                        for btn in categories_buttons.find_all('button', class_='category'):
                            span = btn.find('span')
                            if span:
                                categories_list.append(span.text.strip())
                    categories = '、'.join(categories_list) if categories_list else 'N/A'
                    
                    # 電影圖片 URL（從 img 標籤的 src 提取）
                    img_elem = item.find('img', class_='cover')
                    image_url = img_elem.get('src', 'N/A') if img_elem else 'N/A'
                    
                    movie_data = {
                        '電影名稱': name,
                        '評分': score,
                        '類型': categories,
                        '電影圖片URL': image_url
                    }
                    
                    movies.append(movie_data)
                    
                except Exception as e:
                    continue
            
            time.sleep(1)
            
        except requests.exceptions.RequestException as e:
            progress_placeholder.warning(f"第 {page} 頁爬取失敗: {e}")
            continue
    
    progress_placeholder.empty()
    return pd.DataFrame(movies)

def part1_weather():
    """Part 1 - 天氣預報"""
    st.title("🇹🇼 台灣天氣預報儀表板")

    try:
        matplotlib.rcParams['font.family'] = 'Microsoft JhengHei'
        plt.rcParams['axes.unicode_minus'] = False
    except Exception:
        st.warning("無法設定中文字體 'Microsoft JhengHei'，圖表中的中文可能無法正常顯示。")

    if not os.path.exists(DB_FILE):
        st.warning(f"資料庫檔案 '{os.path.basename(DB_FILE)}' 不存在，將自動執行首次資料更新。")
        if run_update_script(CRAWLER_SCRIPT, f"正在執行 '{CRAWLER_SCRIPT}' 以建立資料庫..."):
            st.success("資料庫已成功建立！頁面將重新載入。")
            st.rerun()
        else:
            st.error("初始化資料庫失敗，應用程式無法啟動。請查看終端機日誌以獲取詳細資訊。")
            return

    if st.button("🔄 更新天氣資料"):
        if run_update_script(CRAWLER_SCRIPT, f"正在從 API 獲取最新資料..."):
            st.success("資料更新成功！")
            st.rerun()
        else:
            st.error("資料更新失敗。")
    
    st.markdown("---")

    df = get_weather_data()

    if df.empty:
        st.info("目前沒有可顯示的資料，請先更新資料。")
        return

    st.header("📋 天氣預報資料表")
    df_display = df.copy()
    df_display['start_time'] = df_display['start_time'].dt.strftime('%m-%d %H:00')
    df_display.rename(columns={
        'location_name': '地點',
        'start_time': '時間',
        'avg_temp': '平均溫度',
        'pop': '降雨機率'
    }, inplace=True)
    
    st.dataframe(df_display[[
        '地點', 
        '時間', 
        '平均溫度', 
        '降雨機率'
    ]], use_container_width=True)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        plot_weather_chart(df, 'avg_temp', '📈 各地區平均溫度趨勢', '溫度 (°C)')
    with col2:
        plot_weather_chart(df, 'pop', '💧 各地區降雨機率趨勢', '降雨機率 (%)')

def part2_movies():
    """Part 2 - 電影爬蟲"""
    st.title("🎬 電影資訊庫")
    st.markdown("爬取自 https://ssr1.scrape.center (第 1-10 頁)")
    
    if st.button("🔄 重新爬取電影資訊", key="refresh_movies"):
        st.cache_data.clear()
        st.rerun()
    
    with st.spinner("正在爬取電影資訊，請耐心等候..."):
        movies_df = scrape_movies()
    
    if not movies_df.empty:
        st.success(f"✅ 成功爬取 {len(movies_df)} 部電影！")
        
        # 保存為 CSV
        csv_file = os.path.join(BASE_DIR, 'movie.csv')
        movies_df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        st.info(f"📁 數據已自動保存到 `movie.csv`")
        
        st.markdown("---")
        st.header("📊 電影資訊表")
        st.dataframe(movies_df, use_container_width=True)
        
        # 提供 CSV 下載按鈕
        csv_data = movies_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 下載為 CSV",
            data=csv_data,
            file_name="movie.csv",
            mime="text/csv"
        )
        
    else:
        st.error("無法爬取電影資訊，請檢查網路連線或稍後重試。")

def main():
    """Streamlit 應用程式主函式。"""
    st.set_page_config(page_title="天氣預報與電影資訊", layout="wide")

    st.sidebar.markdown("# 📑 導航菜單")
    page = st.sidebar.radio(
        "選擇頁面",
        ["Part 1 - 天氣預報", "Part 2 - 電影資訊"]
    )

    if page == "Part 1 - 天氣預報":
        part1_weather()
    elif page == "Part 2 - 電影資訊":
        part2_movies()

if __name__ == "__main__":
    main()
