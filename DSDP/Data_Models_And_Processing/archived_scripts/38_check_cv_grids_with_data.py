"""
檢查高波動網格的數據量
"""
import pandas as pd
import numpy as np

df = pd.read_csv('data1.csv')

# Top 10 高波動網格
grid_features = []

for (x, y), group in df.groupby(['x', 'y']):
    n = group.sort_values(['d', 't'])['n'].values
    
    if len(n) < 100 or n.sum() < 1000:
        continue
    
    mean_val = n.mean()
    std_val = n.std()
    cv = std_val / mean_val if mean_val > 0 else 0
    
    grid_features.append({
        'x': x,
        'y': y,
        'data_length': len(n),
        'total_flow': n.sum(),
        'mean': mean_val,
        'std': std_val,
        'cv': cv
    })

features_df = pd.DataFrame(grid_features)

print("Top 10 最高波動（CV）網格（需要數據量>3600）：")
print("="*80)

top_cv = features_df[features_df['data_length'] >= 3600].nlargest(10, 'cv')

for idx, (i, row) in enumerate(top_cv.iterrows(), 1):
    print(f"{idx:2d}. ({row['x']:3.0f}, {row['y']:3.0f})  CV: {row['cv']:.4f}  "
          f"數據量: {row['data_length']}  平均: {row['mean']:6.2f}")

print(f"\n推薦選擇: ({top_cv.iloc[0]['x']:.0f}, {top_cv.iloc[0]['y']:.0f})")
