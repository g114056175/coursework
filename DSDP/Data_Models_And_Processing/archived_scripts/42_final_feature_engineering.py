"""
完整流程：為最終選定的網格進行特徵工程、訓練和評估

最終網格選擇：
1. (80, 95) - 最高人流（保留已訓練的模型）
2. (80, 93) - 第二高人流（重新訓練）
3. (79, 97) - 最大瞬間湧入（重新訓練）
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import os
import shutil

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
    for lag in [1, 2, 3, 4, 5, 6]:
        features[f'lag_{lag}'] = np.roll(n, lag)
    
    features['lag_48'] = np.roll(n, 48)
    features['lag_96'] = np.roll(n, 96)
    features['lag_336'] = np.roll(n, 336)
    
    # Rolling Statistics
    window = 12
    n_series = pd.Series(n)
    features['rolling_mean'] = n_series.rolling(window, min_periods=1).mean().values
    features['rolling_std'] = n_series.rolling(window, min_periods=1).std().fillna(0).values
    features['rolling_min'] = n_series.rolling(window, min_periods=1).min().values
    features['rolling_max'] = n_series.rolling(window, min_periods=1).max().values
    
    # Time Encoding
    for hour in range(48):
        features[f'hour_{hour}'] = (t == hour).astype(float)
    
    for day in range(7):
        features[f'dow_{day}'] = (d % 7 == day).astype(float)
    
    features['is_weekend'] = ((d % 7 == 5) | (d % 7 == 6)).astype(float)
    features['target'] = n
    
    feature_df = pd.DataFrame(features)
    warmup = 336
    feature_df = feature_df.iloc[warmup:].reset_index(drop=True)
    
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
    print("Step 1: 清理舊檔案")
    print("="*80)
    print()
    
    # 清理 grid_selection 中不需要的時序圖
    to_keep_in_selection = [
        'grid_1_80_95_最高人流.png',
        'grid_79_97_最大瞬間湧入.png',
        'README.md',
        'persistence_confusion_matrix.png',
        'persistence_errors.png',
        'comparison_all_grids.png',
    ]
    
    # 保留選擇理由圖
    to_keep_in_selection.extend([f for f in os.listdir('grid_selection') if f.startswith('selection_justification')])
    
    for f in os.listdir('grid_selection'):
        if f.endswith('.png') and f not in to_keep_in_selection:
            if f.startswith('grid_') and '80_95' not in f and '79_97' not in f:
                print(f"  刪除: grid_selection/{f}")
                os.remove(f'grid_selection/{f}')
    
    print()
    print("="*80)
    print("Step 2: 特徵工程")
    print("="*80)
    print()
    
    df = pd.read_csv('data1.csv')
    
    # 最終網格
    grids = [
        {'rank': 2, 'x': 80, 'y': 93, 'feature': '第二高人流'},
        {'rank': 3, 'x': 79, 'y': 97, 'feature': '最大瞬間湧入'}
    ]
    
    for grid_info in grids:
        rank = grid_info['rank']
        x, y = grid_info['x'], grid_info['y']
        feature = grid_info['feature']
        
        print(f"網格 #{rank}: ({x}, {y}) - {feature}")
        print("-"*80)
        
        feature_df = extract_features_for_grid(df, x, y)
        data_dict = normalize_and_split(feature_df, train_days=60)
        
        data_dict['grid_x'] = x
        data_dict['grid_y'] = y
        data_dict['grid_rank'] = rank
        data_dict['grid_feature'] = feature
        
        threshold = data_dict['train_mean'] + 1.0 * data_dict['train_std']
        data_dict['burst_threshold'] = threshold
        
        print(f"  特徵維度: {len(data_dict['feature_names'])}")
        print(f"  訓練集: {data_dict['X_train'].shape}")
        print(f"  測試集: {data_dict['X_test'].shape}")
        print(f"  爆量門檻: {threshold:.2f}")
        
        output_file = f'resnet_features/grid_{rank}_{x}_{y}.npz'
        np.savez(output_file, **data_dict)
        print(f"  ✓ 已儲存: {output_file}\n")
    
    print("="*80)
    print("✅ 特徵工程完成！接下來需要訓練模型。")
    print("="*80)

if __name__ == '__main__':
    main()
