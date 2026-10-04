# AIOT 作業 6 - 天氣預報與電影資訊儀表板

## 📋 專案概述

這是一個使用 Python、Streamlit 和 SQLite3 構建的雙功能應用程式，提供：
- **Part 1**：台灣天氣預報數據展示（來自中央氣象署 API）
- **Part 2**：電影資訊爬蟲與展示（來自 ssr1.scrape.center）

## 🎯 主要功能

### Part 1 - 天氣預報儀表板
- 🔄 **更新功能**：按鈕點擊可從 CWA API 獲取最新天氣數據
- 📊 **數據表格**：顯示地點、時間、平均溫度、降雨機率
- 📈 **趨勢圖表**：折線圖展示溫度變化趨勢
- 💾 **數據持久化**：使用 SQLite3 存儲數據於 `data.db`

### Part 2 - 電影資訊庫
- 🎬 **網頁爬蟲**：爬取 ssr1.scrape.center 第 1-10 頁電影信息
- 📊 **信息表格**：顯示電影名、上映地區、上映時間、類型、評分
- 🔄 **實時刷新**：支持重新爬取最新電影信息

## 📁 項目結構

```
AIOT_class/
├── app.py                      # Streamlit 主應用程序
├── api_crawler.py              # API 爬蟲腳本
├── movie_crawler.py            # 電影網站爬蟲腳本
├── data.db                     # SQLite3 數據庫（自動生成）
├── conversation.log            # 開發過程記錄
└── README.md                   # 本文件
```

## 🚀 快速開始

### 前置要求
- Python 3.7+
- pip（Python 套件管理工具）

### 安裝依賴

```bash
pip install streamlit pandas sqlite3 matplotlib requests beautifulsoup4 lxml
```

或在虛擬環境中：
```bash
python -m venv .venv
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
```

### 運行應用

```bash
streamlit run app.py
```

應用將在 `http://localhost:8502` 上啟動。

## 🔌 API 配置

### 中央氣象署 (CWA) API
- **端點**：`https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-091`
- **認證**：需要 Authorization 密鑰（已在代碼中配置）
- **數據**：全台灣各地區的溫度、降雨機率等天氣信息

### 電影網站
- **來源**：https://ssr1.scrape.center
- **頁數**：第 1-10 頁
- **爬取內容**：電影名稱、上映地區、上映時間、分類、評分

## 📊 數據流程

```
CWA API / 網頁爬蟲
    ↓
SQLite3 data.db (天氣數據) / 內存 DataFrame (電影數據)
    ↓
Streamlit UI (表格 + 圖表)
    ↓
用戶瀏覽器
```

## 🛠️ 核心功能說明

### 天氣數據更新
1. 點擊「🔄 更新天氣資料」按鈕
2. 應用從 CWA API 爬取最新數據
3. 解析 JSON 並提取需要的欄位
4. 更新 SQLite3 數據庫
5. 自動刷新頁面顯示新數據

### 電影資訊爬取
1. 使用 BeautifulSoup 解析 HTML
2. 提取電影容器 (`div class="item"`)
3. 從 HTML 結構中提取各個欄位：
   - 電影名：`<h2>` 標籤
   - 類型：`<div class="categories">` 中的 `<button>` 標籤
   - 地區和時間：`<div class="info">` 中的 `<span>` 標籤
   - 評分：`<p class="score">` 標籤
4. 轉換為 DataFrame 並在 Streamlit 中顯示

## 🐛 已知問題及解決方案

### SSL 證書驗證錯誤
**問題**：連接 CWA API 時出現 `SSLCertVerificationError`
**解決**：在 `requests.get()` 中添加 `verify=False` 參數

### JSON 路徑解析錯誤
**問題**：API 返回的 JSON 結構與預期不符
**解決**：通過完整的原始 API 回應調試，確認正確路徑為 `data['records']['Locations'][0]['location']`

## 📝 使用說明

### Part 1 - 天氣預報
1. 啟動應用後，自動進入 Part 1
2. 第一次加載時，若無 `data.db` 會自動從 API 獲取數據
3. 使用「更新天氣資料」按鈕手動刷新數據
4. 查看表格和折線圖的溫度變化趨勢

### Part 2 - 電影資訊
1. 在左側邊欄選擇「Part 2 - 電影資訊」
2. 應用自動從 ssr1.scrape.center 爬取 10 頁的電影信息
3. 首次加載可能需要 10-15 秒（爬取 100+ 部電影）
4. 點擊「重新爬取電影資訊」按鈕可刷新數據
5. 在表格中查看電影詳細信息

## 🔧 自定義配置

### 修改 CWA API 密鑰
編輯 `app.py` 中的 `API_URL`：
```python
API_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-091?Authorization=YOUR_KEY"
```

### 修改電影爬蟲頁數
編輯 `app.py` 中 `scrape_movies()` 函數：
```python
for page in range(1, 11):  # 改為你需要的頁數
```

## 📸 DEMO 圖片

### Part 1 - 天氣預報儀表板
![天氣預報界面](img/image1.png)

### Part 2 - 電影資訊爬蟲
![電影資訊表格](img/image2.png)

### 應用交互功能
![應用功能展示](img/image3.png)

---

**最後更新**：2025 年 12 月 4 日
**開發環境**：Python 3.13.7 + Streamlit 1.52.0
