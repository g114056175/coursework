"""
ResNet 時序預測 - 特徵工程

為三個選定網格提取時序特徵：
1. Lag features: t-1 to t-6, t-48, t-96, t-336
2. Rolling statistics: mean, std, min, max (window=12)
3. Time encoding: hour of day, day of week, is weekend
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import json
import os

def extract_features_for_grid(df, x, y):
    """為單個網格提取特徵"""
    
    # 提取該網格數據
    grid_data = df[(df['x'] == x) & (df['y'] == y)].copy()
    grid_data = grid_data.sort_values(['d', 't'])
    
    n = grid_data['n'].values
    d = grid_data['d'].values
    t = grid_data['t'].values
    
    print(f"  數據長度: {len(n)}")
    
    # 初始化特徵字典
    features = {}
    
    # === 1. Lag Features ===
    print("  提取 Lag features...")
    for lag in [1, 2, 3, 4, 5, 6]:
        features[f'lag_{lag}'] = np.roll(n, lag)
    
    # Daily patterns
    features['lag_48'] = np.roll(n, 48)   # Yesterday same time
    features['lag_96'] = np.roll(n, 96)   # 2 days ago
    features['lag_336'] = np.roll(n, 336) # Last week
    
    # === 2. Rolling Statistics ===
    print("  計算 Rolling statistics...")
    window = 12
    
    # Pad with NaN for rolling calculations
    n_series = pd.Series(n)
    features['rolling_mean'] = n_series.rolling(window, min_periods=1).mean().values
    features['rolling_std'] = n_series.rolling(window, min_periods=1).std().fillna(0).values
    features['rolling_min'] = n_series.rolling(window, min_periods=1).min().values
    features['rolling_max'] = n_series.rolling(window, min_periods=1).max().values
    
    # === 3. Time Encoding ===
    print("  創建 Time encoding...")
    
    # Hour of day (0-47) - one-hot
    for hour in range(48):
        features[f'hour_{hour}'] = (t == hour).astype(float)
    
    # Day of week (0-6) - one-hot
    for day in range(7):
        features[f'dow_{day}'] = (d % 7 == day).astype(float)
    
    # Is weekend
    features['is_weekend'] = ((d % 7 == 5) | (d % 7 == 6)).astype(float)
    
    # === 4. Target ===
    features['target'] = n
    
    # 轉換為 DataFrame
    feature_df = pd.DataFrame(features)
    
    # 移除前336個時段的數據（因為 lag_336 需要）
    warmup = 336
    feature_df = feature_df.iloc[warmup:].reset_index(drop=True)
    
    print(f"  特徵維度: {feature_df.shape}")
    print(f"  有效數據: {len(feature_df)} 時段")
    
    return feature_df

def normalize_and_split(feature_df, train_days=60):
    """標準化並分割訓練/測試集"""
    
    train_size = train_days * 48
    
    # 分離特徵和目標
    target_col = 'target'
    feature_cols = [c for c in feature_df.columns if c != target_col]
    
    X = feature_df[feature_cols].values
    y = feature_df[target_col].values
    
    # 分割
    X_train = X[:train_size]
    X_test = X[train_size:]
    y_train = y[:train_size]
    y_test = y[train_size:]
    
    # 標準化（只對數值特徵）
    # 識別數值特徵：lag, rolling
    numerical_cols = [i for i, c in enumerate(feature_cols) 
                     if c.startswith('lag_') or c.startswith('rolling_')]
    
    scaler = StandardScaler()
    if len(numerical_cols) > 0:
        X_train[:, numerical_cols] = scaler.fit_transform(X_train[:, numerical_cols])
        X_test[:, numerical_cols] = scaler.transform(X_test[:, numerical_cols])
    
    print(f"  訓練集: {X_train.shape}, 測試集: {X_test.shape}")
    
    return {
        'X_train': X_train.astype(np.float32),
        'X_test': X_test.astype(np.float32),
        'y_train': y_train.astype(np.float32),
        'y_test': y_test.astype(np.float32),
        'feature_names': feature_cols,
        'scaler': scaler,
        'train_mean': y_train.mean(),
        'train_std': y_train.std()
    }

def main():
    print("="*80)
    print("ResNet 特徵工程")
    print("="*80)
    print()
    
    # 創建輸出目錄
    os.makedirs('resnet_features', exist_ok=True)
    
    # 選定的網格
    selected_grids = [
        {'rank': 1, 'x': 80, 'y': 95, 'feature': '最高人流'},
        {'rank': 2, 'x': 34, 'y': 44, 'feature': '最大瞬間湧入'},
        {'rank': 3, 'x': 86, 'y': 149, 'feature': '最高波動性'}
    ]
    
    # 讀取數據
    print("讀取數據...")
    df = pd.read_csv('data1.csv')
    print(f"原始數據: {df.shape}\n")
    
    # 處理每個網格
    for grid_info in selected_grids:
        rank = grid_info['rank']
        x, y = grid_info['x'], grid_info['y']
        feature = grid_info['feature']
        
        print(f"處理網格 #{rank}: ({x}, {y}) - {feature}")
        print("-"*80)
        
        # 提取特徵
        feature_df = extract_features_for_grid(df, x, y)
        
        # 標準化並分割
        data_dict = normalize_and_split(feature_df, train_days=60)
        
        # 添加網格信息
        data_dict['grid_x'] = x
        data_dict['grid_y'] = y
        data_dict['grid_rank'] = rank
        data_dict['grid_feature'] = feature
        
        # 計算爆量門檻（基於訓練集）
        threshold = data_dict['train_mean'] + 1.0 * data_dict['train_std']
        data_dict['burst_threshold'] = threshold
        
        print(f"  爆量門檻 (1.0σ): {threshold:.2f}")
        
        # 儲存
        output_file = f'resnet_features/grid_{rank}_{x}_{y}.npz'
        np.savez(output_file, **data_dict)
        
        print(f"  ✓ 已儲存: {output_file}\n")
    
    print("="*80)
    print("✅ 特徵工程完成！")
    print("="*80)
    print("\n產生的檔案：")
    for grid_info in selected_grids:
        rank, x, y = grid_info['rank'], grid_info['x'], grid_info['y']
        print(f"  - resnet_features/grid_{rank}_{x}_{y}.npz")
    
    # 儲存特徵資訊
    feature_info = {
        'num_features': len(data_dict['feature_names']),
        'feature_names': data_dict['feature_names'],
        'feature_groups': {
            'lag': [f'lag_{i}' for i in [1,2,3,4,5,6]] + ['lag_48', 'lag_96', 'lag_336'],
            'rolling': ['rolling_mean', 'rolling_std', 'rolling_min', 'rolling_max'],
            'hour_encoding': [f'hour_{i}' for i in range(48)],
            'day_encoding': [f'dow_{i}' for i in range(7)] + ['is_weekend']
        }
    }
    
    with open('resnet_features/feature_info.json', 'w', encoding='utf-8') as f:
        json.dump(feature_info, f, indent=2, ensure_ascii=False)
    
    print(f"\n  - resnet_features/feature_info.json")
    print(f"\n總特徵數: {feature_info['num_features']}")

if __name__ == '__main__':
    main()
