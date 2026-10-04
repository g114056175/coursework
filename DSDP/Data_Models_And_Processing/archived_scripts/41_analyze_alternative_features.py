"""
分析其他網格選擇標準

尋找不與總人流強相關的特徵：
1. 自相關性（Autocorrelation lag-1）：時序依賴性，可預測性指標
2. 日週期性強度（Daily periodicity）：規律性
3. 爆量頻率（Burst frequency）：超過1.0σ的比例
4. 峰谷比（Peak-to-minimum ratio）：動態範圍
5. 活躍時段比例（Activity ratio）：非零時段比例
"""

import pandas as pd
import numpy as np
from scipy import stats

def calculate_autocorr(n, lag=1):
    """計算自相關"""
    if len(n) < lag + 1:
        return 0
    return np.corrcoef(n[:-lag], n[lag:])[0, 1] if len(n) > lag else 0

def calculate_daily_periodicity(n):
    """計算日週期性（lag-48 自相關）"""
    return calculate_autocorr(n, lag=48)

df = pd.read_csv('data1.csv')

print("="*80)
print("分析網格選擇的替代特徵")
print("="*80)
print()

grid_features = []

for (x, y), group in df.groupby(['x', 'y']):
    n = group.sort_values(['d', 't'])['n'].values
    
    if len(n) < 2000:  # 至少約42天數據
        continue
    
    if n.sum() < 1000:  # 最低人流要求（避免數據太少）
        continue
    
    mean_val = n.mean()
    std_val = n.std()
    cv = std_val / mean_val if mean_val > 0 else 0
    
    # 自相關性
    autocorr_1 = calculate_autocorr(n, lag=1)
    autocorr_48 = calculate_daily_periodicity(n)
    
    # 爆量頻率
    threshold = mean_val + 1.0 * std_val
    burst_freq = (n > threshold).sum() / len(n) * 100
    
    # 峰谷比
    peak_to_min = n.max() / n.min() if n.min() > 0 else n.max()
    
    # 活躍時段比例
    activity_ratio = (n > 0).sum() / len(n) * 100
    
    # 數據完整性
    zero_pct = (n == 0).sum() / len(n) * 100
    
    grid_features.append({
        'x': x,
        'y': y,
        'total_flow': n.sum(),
        'mean': mean_val,
        'cv': cv,
        'autocorr_1': autocorr_1,
        'autocorr_48': autocorr_48,
        'burst_freq': burst_freq,
        'peak_to_min': peak_to_min,
        'activity_ratio': activity_ratio,
        'zero_pct': zero_pct,
        'data_length': len(n)
    })

features_df = pd.DataFrame(grid_features)

print(f"符合條件的網格數: {len(features_df)}\n")

# 計算與總人流的相關性
print("各特徵與總人流的相關係數：")
print("-"*80)
correlations = {}
for col in ['cv', 'autocorr_1', 'autocorr_48', 'burst_freq', 'peak_to_min', 'activity_ratio']:
    corr = features_df['total_flow'].corr(features_df[col])
    correlations[col] = abs(corr)
    print(f"{col:20s}: {corr:+.3f}  (絕對值: {abs(corr):.3f})")

print()

# 找出相關性最低的特徵（排除 total_flow）
sorted_by_corr = sorted(correlations.items(), key=lambda x: x[1])
print("推薦使用的特徵（與總人流相關性由低到高）：")
print("-"*80)
for i, (feature, corr) in enumerate(sorted_by_corr[:5], 1):
    print(f"{i}. {feature:20s} - 相關性: {corr:.3f}")

print("\n" + "="*80)

# 對於前3個低相關性特徵，顯示 Top 10
for feature_name, _ in sorted_by_corr[:3]:
    print(f"\n{feature_name.upper()} - Top 10:")
    print("-"*80)
    
    top_10 = features_df.nlargest(10, feature_name)
    
    for idx, (i, row) in enumerate(top_10.iterrows(), 1):
        marker = ""
        if row['x'] == 80 and row['y'] == 95:
            marker = " (網格1: 最高人流)"
        elif row['x'] == 79 and row['y'] == 97:
            marker = " (網格2候選: 最大增幅)"
        elif row['x'] == 86 and row['y'] == 149:
            marker = " (網格3: 高波動)"
        
        print(f"{idx:2d}. ({row['x']:3.0f}, {row['y']:3.0f})  "
              f"{feature_name}={row[feature_name]:6.2f}  "
              f"人流={row['total_flow']:,}  "
              f"平均={row['mean']:5.2f}{marker}")

print("\n" + "="*80)
print("建議選擇標準")
print("="*80)

# 找出一個合適的第三網格
print("\n最佳候選（綜合考量低相關性 + 足夠數據）：")

# 選擇自相關性或爆量頻率
for feature_name in ['autocorr_1', 'burst_freq', 'autocorr_48']:
    if feature_name in [f[0] for f in sorted_by_corr[:3]]:
        top_candidate = features_df.nlargest(1, feature_name)
        if len(top_candidate) > 0:
            row = top_candidate.iloc[0]
            print(f"\n使用 '{feature_name}':")
            print(f"  網格: ({row['x']:.0f}, {row['y']:.0f})")
            print(f"  {feature_name}: {row[feature_name]:.3f}")
            print(f"  總人流: {row['total_flow']:,}")
            print(f"  平均: {row['mean']:.2f}")
            print(f"  數據長度: {row['data_length']}")
        break
