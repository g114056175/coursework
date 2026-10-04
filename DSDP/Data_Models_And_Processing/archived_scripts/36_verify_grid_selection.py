"""
全面驗證三個網格的選擇標準

檢查：
1. 最高累積人流
2. 最大瞬間增幅
3. 最高變異係數（波動性）
"""

import pandas as pd
import numpy as np

df = pd.read_csv('data1.csv')

print("="*80)
print("全面驗證網格選擇")
print("="*80)

# 計算所有網格的特徵
grid_features = []

for (x, y), group in df.groupby(['x', 'y']):
    group = group.sort_values(['d', 't'])
    n = group['n'].values
    
    if len(n) < 100 or n.sum() < 1000:
        continue
    
    mean_val = n.mean()
    std_val = n.std()
    cv = std_val / mean_val if mean_val > 0 else 0
    
    changes = np.diff(n)
    max_increase = changes.max() if len(changes) > 0 else 0
    
    grid_features.append({
        'x': x,
        'y': y,
        'total_flow': n.sum(),
        'mean': mean_val,
        'std': std_val,
        'cv': cv,
        'max_increase': max_increase
    })

features_df = pd.DataFrame(grid_features)

print(f"\n有效網格數: {len(features_df)}\n")

# === 1. 最高累積人流 ===
print("="*80)
print("標準1: 最高累積人流")
print("="*80)

top_flow = features_df.nlargest(10, 'total_flow')
print("\nTop 10 最高累積人流：")
for idx, (i, row) in enumerate(top_flow.iterrows(), 1):
    marker = " ⭐ 目前選擇" if (row['x'] == 80 and row['y'] == 95) else ""
    print(f"{idx:2d}. ({row['x']:3.0f}, {row['y']:3.0f})  人流: {row['total_flow']:,}{marker}")

# === 2. 最大瞬間增幅 ===
print("\n" + "="*80)
print("標準2: 最大瞬間增幅")
print("="*80)

top_increase = features_df.nlargest(10, 'max_increase')
print("\nTop 10 最大增幅：")
for idx, (i, row) in enumerate(top_increase.iterrows(), 1):
    marker = " ⭐ 目前選擇" if (row['x'] == 34 and row['y'] == 44) else ""
    print(f"{idx:2d}. ({row['x']:3.0f}, {row['y']:3.0f})  增幅: +{row['max_increase']:3.0f}  "
          f"累積人流: {row['total_flow']:,}{marker}")

# === 3. 最高變異係數 ===
print("\n" + "="*80)
print("標準3: 最高變異係數（波動性）")
print("="*80)

top_cv = features_df.nlargest(10, 'cv')
print("\nTop 10 最高變異係數：")
for idx, (i, row) in enumerate(top_cv.iterrows(), 1):
    marker = " ⭐ 目前選擇" if (row['x'] == 86 and row['y'] == 149) else ""
    print(f"{idx:2d}. ({row['x']:3.0f}, {row['y']:3.0f})  CV: {row['cv']:.4f}  "
          f"平均: {row['mean']:6.2f}  標準差: {row['std']:6.2f}{marker}")

# === 檢查用戶提到的網格 ===
print("\n" + "="*80)
print("檢查用戶提到的網格")
print("="*80)

check_grids = [
    (85, 75, "用戶提到的高波動網格"),
    (79, 97, "真正的最大增幅網格"),
]

for x, y, desc in check_grids:
    grid_row = features_df[(features_df['x'] == x) & (features_df['y'] == y)]
    if len(grid_row) > 0:
        row = grid_row.iloc[0]
        print(f"\n網格 ({x}, {y}) - {desc}")
        print(f"  累積人流: {row['total_flow']:,}")
        print(f"  平均: {row['mean']:.2f}")
        print(f"  標準差: {row['std']:.2f}")
        print(f"  變異係數: {row['cv']:.4f}")
        print(f"  最大增幅: +{row['max_increase']:.0f}")
        
        # 排名
        flow_rank = (features_df['total_flow'] > row['total_flow']).sum() + 1
        increase_rank = (features_df['max_increase'] > row['max_increase']).sum() + 1
        cv_rank = (features_df['cv'] > row['cv']).sum() + 1
        
        print(f"  排名: 人流第{flow_rank}, 增幅第{increase_rank}, 波動第{cv_rank}")
    else:
        print(f"\n網格 ({x}, {y}) - 無數據")

# === 總結 ===
print("\n" + "="*80)
print("選擇建議")
print("="*80)

best_flow = top_flow.iloc[0]
best_increase = top_increase.iloc[0]
best_cv = top_cv.iloc[0]

print(f"\n建議選擇：")
print(f"1. 最高人流: ({best_flow['x']:.0f}, {best_flow['y']:.0f}) - {best_flow['total_flow']:,}")
print(f"2. 最大增幅: ({best_increase['x']:.0f}, {best_increase['y']:.0f}) - +{best_increase['max_increase']:.0f}")
print(f"3. 最高波動: ({best_cv['x']:.0f}, {best_cv['y']:.0f}) - CV={best_cv['cv']:.4f}")

print(f"\n目前選擇：")
print(f"1. 最高人流: (80, 95) {'✅ 正確' if best_flow['x'] == 80 and best_flow['y'] == 95 else '❌ 錯誤'}")
print(f"2. 最大增幅: (34, 44) {'✅ 正確' if best_increase['x'] == 34 and best_increase['y'] == 44 else '❌ 錯誤'}")
print(f"3. 最高波動: (86, 149) {'✅ 正確' if best_cv['x'] == 86 and best_cv['y'] == 149 else '❌ 錯誤'}")
