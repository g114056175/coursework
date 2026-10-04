"""
重新選擇網格 - 強調多樣性

選擇標準：
1. 地理位置分散（避免聚集）
2. 人流量級差異（高、中、低）
3. 時序模式多樣化
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json

plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def find_diverse_grids():
    """尋找具有多樣性的網格"""
    
    df = pd.read_csv('data1.csv')
    
    # 計算每個網格的累積人流和統計特徵
    print("分析所有網格...")
    grid_stats = []
    
    for (x, y), group in df.groupby(['x', 'y']):
        n = group['n'].values
        
        if len(n) < 100 or n.sum() < 1000:  # 過濾掉數據太少的網格
            continue
        
        mean_val = n.mean()
        std_val = n.std()
        cv = std_val / mean_val if mean_val > 0 else 0
        autocorr = np.corrcoef(n[:-1], n[1:])[0, 1] if len(n) > 1 else 0
        
        grid_stats.append({
            'x': x,
            'y': y,
            'total_flow': n.sum(),
            'mean': mean_val,
            'std': std_val,
            'cv': cv,
            'autocorr': autocorr,
            'zero_pct': (n == 0).sum() / len(n) * 100
        })
    
    grid_df = pd.DataFrame(grid_stats).sort_values('total_flow', ascending=False)
    
    print(f"符合條件的網格數: {len(grid_df)}")
    
    # 按人流量分組
    grid_df['flow_tier'] = pd.cut(grid_df['total_flow'], 
                                   bins=[0, 50000, 100000, float('inf')],
                                   labels=['低', '中', '高'])
    
    print(f"\n人流分布:")
    print(grid_df['flow_tier'].value_counts().sort_index())
    
    return grid_df

def select_diverse_set(grid_df):
    """選擇多樣化的三個網格"""
    
    print(f"\n{'='*80}")
    print("多樣性網格選擇策略")
    print(f"{'='*80}\n")
    
    candidates = []
    
    # 策略 1: 一個高人流 + 一個中人流 + 一個偏遠/特殊模式
    
    # 高人流區（Top 10 中選一個最佳）
    high_flow = grid_df.head(10).copy()
    high_flow['score'] = (
        high_flow['autocorr'] * 40 +  # 可預測性
        (1 - high_flow['cv'].clip(0, 2) / 2) * 30 +  # 穩定性
        (1 - high_flow['zero_pct'] / 100) * 30  # 完整性
    )
    best_high = high_flow.nlargest(1, 'score').iloc[0]
    
    candidates.append({
        'tier': '高人流核心區',
        'reason': '人流最高且時序特徵優秀',
        **best_high.to_dict()
    })
    
    print(f"選擇 1: 高人流核心區")
    print(f"  網格: ({best_high['x']:.0f}, {best_high['y']:.0f})")
    print(f"  總人流: {best_high['total_flow']:,.0f}")
    print(f"  特徵: 穩定且可預測\n")
    
    # 中人流區（遠離高人流區，並有好的可預測性）
    mid_flow = grid_df[(grid_df['total_flow'] >= 50000) & 
                       (grid_df['total_flow'] < 100000)].copy()
    
    # 計算與已選網格的距離
    mid_flow['distance'] = np.sqrt(
        (mid_flow['x'] - best_high['x'])**2 + 
        (mid_flow['y'] - best_high['y'])**2
    )
    
    # 選擇距離較遠且特徵好的
    mid_flow = mid_flow[mid_flow['distance'] > 10]  # 至少距離 10 個單位
    
    if len(mid_flow) > 0:
        mid_flow['score'] = (
            mid_flow['autocorr'] * 30 +
            mid_flow['distance'] / mid_flow['distance'].max() * 30 +  # 地理多樣性
            (1 - mid_flow['zero_pct'] / 100) * 20 +
            (mid_flow['total_flow'] / mid_flow['total_flow'].max()) * 20
        )
        best_mid = mid_flow.nlargest(1, 'score').iloc[0]
    else:
        # 如果沒有符合的，從所有中流量中選
        mid_flow = grid_df[(grid_df['total_flow'] >= 50000) & 
                          (grid_df['total_flow'] < 100000)].copy()
        best_mid = mid_flow.iloc[0] if len(mid_flow) > 0 else grid_df.iloc[10]
    
    candidates.append({
        'tier': '中人流過渡區',
        'reason': '遠離核心區，人流適中',
        **best_mid.to_dict()
    })
    
    print(f"選擇 2: 中人流過渡區")
    print(f"  網格: ({best_mid['x']:.0f}, {best_mid['y']:.0f})")
    print(f"  總人流: {best_mid['total_flow']:,.0f}")
    print(f"  與選擇1距離: {np.sqrt((best_mid['x']-best_high['x'])**2 + (best_mid['y']-best_high['y'])**2):.1f}\n")
    
    # 第三個：尋找有特殊模式的（可能是低流量但有趣的模式）
    # 排除已選的附近區域
    remaining = grid_df.copy()
    remaining['dist1'] = np.sqrt((remaining['x'] - best_high['x'])**2 + 
                                 (remaining['y'] - best_high['y'])**2)
    remaining['dist2'] = np.sqrt((remaining['x'] - best_mid['x'])**2 + 
                                 (remaining['y'] - best_mid['y'])**2)
    
    # 至少距離兩個已選網格都有一定距離
    remaining = remaining[(remaining['dist1'] > 5) & (remaining['dist2'] > 5)]
    
    # 選擇一個有良好可預測性且地理多樣的
    if len(remaining) > 0:
        remaining['score'] = (
            remaining['autocorr'] * 30 +  # 可預測性
            (remaining['dist1'] + remaining['dist2']) / 
            (remaining['dist1'].max() + remaining['dist2'].max()) * 40 +  # 地理多樣性
            (1 - remaining['zero_pct'] / 100) * 20 +  # 數據完整性
            (remaining['total_flow'] / grid_df['total_flow'].max()) * 10  # 適量人流
        )
        best_third = remaining.nlargest(1, 'score').iloc[0]
    else:
        best_third = grid_df.iloc[20]
    
    candidates.append({
        'tier': '多樣性補充區',
        'reason': '地理位置獨立，提供不同視角',
        **best_third.to_dict()
    })
    
    print(f"選擇 3: 多樣性補充區")
    print(f"  網格: ({best_third['x']:.0f}, {best_third['y']:.0f})")
    print(f"  總人流: {best_third['total_flow']:,.0f}")
    print(f"  與選擇1距離: {np.sqrt((best_third['x']-best_high['x'])**2 + (best_third['y']-best_high['y'])**2):.1f}")
    print(f"  與選擇2距離: {np.sqrt((best_third['x']-best_mid['x'])**2 + (best_third['y']-best_mid['y'])**2):.1f}")
    
    return pd.DataFrame(candidates)

def visualize_diverse_selection(grid_df, selected):
    """視覺化多樣性選擇"""
    
    fig, axes = plt.subplots(1, 2, figsize=(18, 7))
    
    # 1. 空間分布圖
    ax = axes[0]
    
    # 所有網格（灰色小點）
    ax.scatter(grid_df['x'], grid_df['y'], s=10, c='lightgray', alpha=0.3, label='其他網格')
    
    # Top 10 高人流（橘色）
    top10 = grid_df.head(10)
    ax.scatter(top10['x'], top10['y'], s=100, c='orange', alpha=0.5, 
              edgecolors='black', linewidths=1, label='Top 10 高人流', zorder=5)
    
    # 選中的三個（大星星）
    colors = ['gold', 'lime', 'cyan']
    markers = ['*', 's', 'D']
    
    for idx, row in selected.iterrows():
        ax.scatter(row['x'], row['y'], s=800, marker=markers[idx], 
                  c=colors[idx], edgecolors='black', linewidths=3, 
                  label=f"選擇{idx+1}: {row['tier']}", zorder=10)
        
        ax.annotate(f"選擇{idx+1}\n({row['x']:.0f},{row['y']:.0f})\n{row['total_flow']/1000:.0f}K",
                   xy=(row['x'], row['y']), xytext=(15, 15), 
                   textcoords='offset points', fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle='round', facecolor=colors[idx], alpha=0.8),
                   arrowprops=dict(arrowstyle='->', lw=2))
    
    ax.set_xlabel('X 座標', fontsize=12)
    ax.set_ylabel('Y 座標', fontsize=12)
    ax.set_title('多樣性網格選擇 - 空間分布', fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=9)
    ax.grid(True, alpha=0.3)
    
    # 2. 特徵對比
    ax = axes[1]
    
    categories = ['人流量\n(正規化)', '穩定性\n(1-CV)', 'Lag-1\n自相關', '數據\n完整性']
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]
    
    ax = plt.subplot(122, projection='polar')
    
    for idx, row in selected.iterrows():
        values = [
            row['total_flow'] / grid_df['total_flow'].max(),
            1 - min(1, row['cv']),
            row['autocorr'],
            1 - row['zero_pct'] / 100
        ]
        values += values[:1]
        
        ax.plot(angles, values, 'o-', linewidth=2.5, label=f"選擇{idx+1}: {row['tier']}", 
               color=colors[idx], markersize=8)
        ax.fill(angles, values, alpha=0.2, color=colors[idx])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=10)
    ax.set_ylim(0, 1)
    ax.set_title('三個網格特徵對比', fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=9)
    ax.grid(True)
    
    plt.tight_layout()
    return fig

def main():
    print("="*80)
    print("多樣性網格選擇分析")
    print("="*80)
    print()
    
    # 分析所有網格
    grid_df = find_diverse_grids()
    
    # 選擇多樣化的三個
    selected = select_diverse_set(grid_df)
    
    # 視覺化
    fig = visualize_diverse_selection(grid_df, selected)
    fig.savefig('results/diverse_grid_selection.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    
    print(f"\n{'='*80}")
    print("✅ 分析完成")
    print(f"{'='*80}\n")
    
    print("推薦的多樣化網格:")
    for idx, row in selected.iterrows():
        print(f"\n選擇 {idx+1}: ({row['x']:.0f}, {row['y']:.0f}) - {row['tier']}")
        print(f"  人流量: {row['total_flow']:,.0f}")
        print(f"  人流等級: {row['flow_tier']}")
        print(f"  自相關: {row['autocorr']:.3f}")
        print(f"  理由: {row['reason']}")
    
    # 儲存結果
    output = {
        'selected_grids': [
            {
                'rank': idx + 1,
                'x': int(row['x']),
                'y': int(row['y']),
                'tier': row['tier'],
                'total_flow': int(row['total_flow']),
                'reason': row['reason']
            }
            for idx, row in selected.iterrows()
        ]
    }
    
    with open('results/diverse_grids_final.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print("\n✓ 結果已儲存:")
    print("  - results/diverse_grid_selection.png")
    print("  - results/diverse_grids_final.json")

if __name__ == '__main__':
    main()
