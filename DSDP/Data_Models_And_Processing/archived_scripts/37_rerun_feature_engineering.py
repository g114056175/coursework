"""
為正確的網格重新進行特徵工程

更新網格選擇：
- 網格1: (80, 95) - 最高人流 ✅ 正確
- 網格2: (79, 97) - 最大增幅 ⭐ 更新
- 網格3: (89, 79) - 最高波動 ⭐ 更新
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import json
import os

def extract_features_for_grid(df, x, y):
    """為單個網格提取特徵"""
    
    grid_data = df[(df['x'] == x) & (df['y'] == y)].copy()
    grid_data = grid_data.sort_values(['d', 't'])
    
    n = grid_data['n'].values
    d = grid_data['d'].values
    t = grid_data['t'].values
    
    print(f"  數據長度: {len(n)}")
    
    features = {}
    
    # Lag Features
    print("  提取 Lag features...")
    for lag in [1, 2, 3, 4, 5, 6]:
        features[f'lag_{lag}'] = np.roll(n, lag)
    
    features['lag_48'] = np.roll(n, 48)
    features['lag_96'] = np.roll(n, 96)
    features['lag_336'] = np.roll(n, 336)
    
    # Rolling Statistics
    print("  計算 Rolling statistics...")
    window = 12
    
    n_series = pd.Series(n)
    features['rolling_mean'] = n_series.rolling(window, min_periods=1).mean().values
    features['rolling_std'] = n_series.rolling(window, min_periods=1).std().fillna(0).values
    features['rolling_min'] = n_series.rolling(window, min_periods=1).min().values
    features['rolling_max'] = n_series.rolling(window, min_periods=1).max().values
    
    # Time Encoding
    print("  創建 Time encoding...")
    
    for hour in range(48):
        features[f'hour_{hour}'] = (t == hour).astype(float)
    
    for day in range(7):
        features[f'dow_{day}'] = (d % 7 == day).astype(float)
    
    features['is_weekend'] = ((d % 7 == 5) | (d % 7 == 6)).astype(float)
    
    features['target'] = n
    
    feature_df = pd.DataFrame(features)
    
    warmup = 336
    feature_df = feature_df.iloc[warmup:].reset_index(drop=True)
    
    print(f"  特徵維度: {feature_df.shape}")
    print(f"  有效數據: {len(feature_df)} 時段")
    
    return feature_df

def normalize_and_split(feature_df, train_days=60):
    """標準化並分割"""
    
    train_size = train_days * 48
    
    target_col = 'target'
    feature_cols = [c for c in feature_df.columns if c != target_col]
    
    X = feature_df[feature_cols].values
    y = feature_df[target_col].values
    
    X_train = X[:train_size]
    X_test = X[train_size:]
    y_train = y[:train_size]
    y_test = y[train_size:]
    
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
    print("重新進行特徵工程（更正後的網格）")
    print("="*80)
    print()
    
    # 更新的網格選擇
    selected_grids = [
        {'rank': 2, 'x': 79, 'y': 97, 'feature': '最大瞬間湧入'},
        {'rank': 3, 'x': 89, 'y': 79, 'feature': '最高波動性'}
    ]
    
    df = pd.read_csv('data1.csv')
    print(f"原始數據: {df.shape}\n")
    
    for grid_info in selected_grids:
        rank = grid_info['rank']
        x, y = grid_info['x'], grid_info['y']
        feature = grid_info['feature']
        
        print(f"處理網格 #{rank}: ({x}, {y}) - {feature}")
        print("-"*80)
        
        feature_df = extract_features_for_grid(df, x, y)
        data_dict = normalize_and_split(feature_df, train_days=60)
        
        data_dict['grid_x'] = x
        data_dict['grid_y'] = y
        data_dict['grid_rank'] = rank
        data_dict['grid_feature'] = feature
        
        threshold = data_dict['train_mean'] + 1.0 * data_dict['train_std']
        data_dict['burst_threshold'] = threshold
        
        print(f"  爆量門檻 (1.0σ): {threshold:.2f}")
        
        # 覆蓋原有檔案
        output_file = f'resnet_features/grid_{rank}_{x}_{y}.npz'
        np.savez(output_file, **data_dict)
        
        print(f"  ✓ 已儲存（覆蓋）: {output_file}\n")
    
    print("="*80)
    print("✅ 特徵工程完成！")
    print("="*80)

if __name__ == '__main__':
    main()
