import json
import requests
import sqlite3
import csv
import os

# 設定 API URL (使用您的 Resource ID)
API_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-091?Authorization=CWA-1FFDDAEC-161F-46A3-BE71-93C32C52829F"
DB_NAME = 'data.db'
CSV_FILE = 'weather_data.csv'

def fetch_raw_data():
    """
    1. Extract: 從 CWA API 獲取原始資料
    """
    try:
        print(f"正在從 CWA API 獲取最新原始資料...")
        # 關閉 SSL 警告
        requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(API_URL, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"錯誤：網路請求失敗 - {e}")
        return None

def process_data(data):
    """
    2. Transform: 清洗與轉置資料
    將巢狀 JSON 轉換為扁平的列表 (List of Dictionaries)
    """
    if not data or 'records' not in data:
        print("無有效資料可處理")
        return []

    locations = data['records']['Locations'][0]['Location']
    all_records = [] # 用來暫存所有整理好的資料
    
    for loc in locations:
        loc_name = loc['LocationName']
        weather_elements = loc['WeatherElement']
        
        # 暫存該地點的時間序列資料
        # Key: start_time, Value: dict containing columns
        forecasts = {} 

        for element in weather_elements:
            element_name = element['ElementName']
            time_slots = element['Time']
            
            for slot in time_slots:
                start_time = slot['StartTime']
                end_time = slot['EndTime']
                
                # 初始化該時段
                if start_time not in forecasts:
                    forecasts[start_time] = {
                        'location_name': loc_name,
                        'start_time': start_time,
                        'end_time': end_time,
                        'avg_temp': None,
                        'max_temp': None,
                        'min_temp': None,
                        'pop': 0, # 預設降雨機率為 0
                        'weather_desc': None,
                        'weather_code': None
                    }
                
                # 取得數值
                values = slot['ElementValue'][0]
                
                # 根據不同因子填入資料
                if element_name == '平均溫度':
                    forecasts[start_time]['avg_temp'] = values.get('Temperature')
                elif element_name == '最高溫度':
                    forecasts[start_time]['max_temp'] = values.get('MaxTemperature')
                elif element_name == '最低溫度':
                    forecasts[start_time]['min_temp'] = values.get('MinTemperature')
                elif element_name == '12小時降雨機率':
                    pop_val = values.get('ProbabilityOfPrecipitation')
                    # 處理非數字的情況 (例如 "-")
                    forecasts[start_time]['pop'] = pop_val if pop_val and pop_val.isdigit() else 0
                elif element_name == '天氣現象':
                    forecasts[start_time]['weather_desc'] = values.get('Weather')
                    forecasts[start_time]['weather_code'] = values.get('WeatherCode')

        # 將該地點整理好的資料加入總列表
        # 依照時間排序，確保 CSV 看起來是順序的
        sorted_forecasts = sorted(forecasts.values(), key=lambda x: x['start_time'])
        all_records.extend(sorted_forecasts)

    return all_records

def save_to_db(records):
    """
    3-1. Load to DB: 存入 SQLite
    """
    if not records:
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 建立表格
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_forecast (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_name TEXT,
            start_time TEXT,
            end_time TEXT,
            avg_temp INTEGER,
            max_temp INTEGER,
            min_temp INTEGER,
            pop INTEGER,
            weather_desc TEXT,
            weather_code TEXT,
            UNIQUE(location_name, start_time) ON CONFLICT REPLACE
        )
    ''')
    
    # 批量寫入
    data_tuples = [
        (r['location_name'], r['start_time'], r['end_time'], 
         r['avg_temp'], r['max_temp'], r['min_temp'], 
         r['pop'], r['weather_desc'], r['weather_code']) 
        for r in records
    ]
    
    cursor.executemany('''
        INSERT INTO weather_forecast 
        (location_name, start_time, end_time, avg_temp, max_temp, min_temp, pop, weather_desc, weather_code)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', data_tuples)
    
    conn.commit()
    conn.close()
    print(f"[DB] 已成功更新 {len(records)} 筆資料至 '{DB_NAME}'")

def save_to_csv(records):
    """
    3-2. Load to CSV: 存入 CSV 檔案
    """
    if not records:
        return

    # 定義 CSV 的欄位順序 (中文 Header 方便查看)
    headers = ['地點', '開始時間', '結束時間', '平均溫度', '最高溫度', '最低溫度', '降雨機率(%)', '天氣現象', '天氣代碼']
    
    # 對應 records 中的 key
    keys = ['location_name', 'start_time', 'end_time', 'avg_temp', 'max_temp', 'min_temp', 'pop', 'weather_desc', 'weather_code']

    try:
        with open(CSV_FILE, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(headers) # 寫入標題
            
            for r in records:
                row = [r[k] for k in keys]
                writer.writerow(row)
                
        print(f"[CSV] 已成功匯出 {len(records)} 筆資料至 '{CSV_FILE}'")
    except Exception as e:
        print(f"無法寫入 CSV: {e}")

def main():
    # 1. 爬取
    raw_data = fetch_raw_data()
    
    if raw_data:
        # 2. 整理
        clean_records = process_data(raw_data)
        print(f"資料整理完成，共 {len(clean_records)} 筆。")
        
        # 3. 儲存 (雙軌進行)
        save_to_db(clean_records)
        save_to_csv(clean_records)

if __name__ == "__main__":
    main()