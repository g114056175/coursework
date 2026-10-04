"""
基於明確特徵指標選擇網格

特徵指標：
1. 最高累積人流
2. 最大瞬間變化（單時段最大增幅）
3. 最高波動性（變異係數最大）
4. 最穩定（變異係數最小但人流高）
5. 最大峰值（單時段最高人數）

選擇條件：彼此距離 > 20 單位
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json

plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def calculate_grid_features():
    """計算每個網格的特徵指標"""
    
    print("讀取數據並計算特徵指標...")
    df = pd.read_csv('data1.csv')
    
    features = []
    
    for (x, y), group in df.groupby(['x', 'y']):
        group = group.sort_values(['d', 't'])
        n = group['n'].values
        
        if len(n) < 100 or n.sum() < 1000:
            continue
        
        # 基本統計
        total_flow = n.sum()
        mean_val = n.mean()
        std_val = n.std()
        max_val = n.max()
        cv = std_val / mean_val if mean_val > 0 else 0
        
        # 瞬間變化（相鄰時段差值）
        changes = np.diff(n)
        max_increase = changes.max() if len(changes) > 0 else 0
        max_decrease = abs(changes.min()) if len(changes) > 0 else 0
        avg_change = np.mean(np.abs(changes)) if len(changes) > 0 else 0
        
        # 爆量事件
        threshold = mean_val + 1.0 * std_val
        burst_count = (n > threshold).sum()
        burst_pct = burst_count / len(n) * 100
        
        features.append({
            'x': x,
            'y': y,
            'total_flow': total_flow,
            'mean': mean_val,
            'std': std_val,
            'cv': cv,
            'max_peak': max_val,
            'max_increase': max_increase,
            'max_decrease': max_decrease,
            'avg_change': avg_change,
            'burst_pct': burst_pct
        })
    
    return pd.DataFrame(features)

def find_characteristic_grids(features_df):
    """找出具有明確特徵的網格"""
    
    print(f"\n{'='*80}")
    print("基於明確特徵指標的網格選擇")
    print(f"{'='*80}\n")
    
    # 過濾：只考慮人流 > 20K 的網格（確保有足夠數據）
    candidates = features_df[features_df['total_flow'] > 20000].copy()
    
    print(f"符合基本條件的網格數: {len(candidates)}\n")
    
    # 定義候選特徵
    characteristic_grids = {}
    
    # 1. 最高累積人流
    top_flow = candidates.nlargest(1, 'total_flow').iloc[0]
    characteristic_grids['最高人流'] = {
        'x': top_flow['x'],
        'y': top_flow['y'],
        'reason': f'累積人流最高 ({top_flow["total_flow"]:,.0f})',
        'value': top_flow['total_flow'],
        **top_flow.to_dict()
    }
    
    # 2. 最大瞬間增幅
    top_increase = candidates.nlargest(1, 'max_increase').iloc[0]
    characteristic_grids['最大湧入'] = {
        'x': top_increase['x'],
        'y': top_increase['y'],
        'reason': f'單時段最大增幅 (+{top_increase["max_increase"]:.0f} 人)',
        'value': top_increase['max_increase'],
        **top_increase.to_dict()
    }
    
    # 3. 最大瞬間減幅
    top_decrease = candidates.nlargest(1, 'max_decrease').iloc[0]
    characteristic_grids['最大散去'] = {
        'x': top_decrease['x'],
        'y': top_decrease['y'],
        'reason': f'單時段最大減幅 (-{top_decrease["max_decrease"]:.0f} 人)',
        'value': top_decrease['max_decrease'],
        **top_decrease.to_dict()
    }
    
    # 4. 最高峰值
    top_peak = candidates.nlargest(1, 'max_peak').iloc[0]
    characteristic_grids['最高峰值'] = {
        'x': top_peak['x'],
        'y': top_peak['y'],
        'reason': f'單時段最高人數 ({top_peak["max_peak"]:.0f} 人)',
        'value': top_peak['max_peak'],
        **top_peak.to_dict()
    }
    
    # 5. 最高波動性
    top_volatile = candidates.nlargest(1, 'cv').iloc[0]
    characteristic_grids['最高波動'] = {
        'x': top_volatile['x'],
        'y': top_volatile['y'],
        'reason': f'變異係數最高 (CV={top_volatile["cv"]:.2f})',
        'value': top_volatile['cv'],
        **top_volatile.to_dict()
    }
    
    # 6. 最穩定（高人流但低 CV）
    high_flow_stable = candidates[candidates['total_flow'] > 50000].copy()
    if len(high_flow_stable) > 0:
        top_stable = high_flow_stable.nsmallest(1, 'cv').iloc[0]
        characteristic_grids['高流量穩定'] = {
            'x': top_stable['x'],
            'y': top_stable['y'],
            'reason': f'高人流但穩定 (CV={top_stable["cv"]:.2f})',
            'value': top_stable['cv'],
            **top_stable.to_dict()
        }
    
    # 顯示所有候選
    print("候選網格特徵:")
    print("-"*80)
    for name, grid in characteristic_grids.items():
        print(f"{name:<15} ({grid['x']:.0f}, {grid['y']:.0f}){'':<10} {grid['reason']}")
    
    return characteristic_grids

def select_final_three(characteristic_grids, features_df):
    """從候選中選擇三個，確保地理分散"""
    
    print(f"\n{'='*80}")
    print("選擇最終三個網格（目標距離 > 15）")
    print(f"{'='*80}\n")
    
    def calc_distance(x1, y1, x2, y2):
        return np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    
    selected = []
    
    # 策略：逐步選擇，確保距離
    
    # 1. 先選最高人流（這是最重要的）
    grid = characteristic_grids['最高人流'].copy()
    grid['feature'] = '最高人流'
    selected.append(grid)
    print(f"  ✅ 選擇 #1: 最高人流 ({grid['x']:.0f}, {grid['y']:.0f}) - {grid['reason']}")
    
    # 2. 從其他候選中選擇距離足夠遠的
    candidates_df = features_df[features_df['total_flow'] > 20000].copy()
    
    # 計算與已選網格的距離
    candidates_df['min_dist'] = candidates_df.apply(
        lambda row: min([calc_distance(row['x'], row['y'], s['x'], s['y']) for s in selected]),
        axis=1
    )
    
    # 找出距離 > 15 的候選
    far_enough = candidates_df[candidates_df['min_dist'] > 15].copy()
    
    if len(far_enough) > 0:
        # 選擇最大湧入（如果夠遠）
        best_increase = far_enough.nlargest(1, 'max_increase').iloc[0]
        grid2 = {
            'x': best_increase['x'],
            'y': best_increase['y'],
            'feature': '最大瞬間湧入',
            'reason': f'單時段最大增幅 (+{best_increase["max_increase"]:.0f} 人)',
            **best_increase.to_dict()
        }
        selected.append(grid2)
        print(f"  ✅ 選擇 #2: 最大瞬間湧入 ({grid2['x']:.0f}, {grid2['y']:.0f}) - {grid2['reason']}")
        
        # 更新距離
        candidates_df['min_dist'] = candidates_df.apply(
            lambda row: min([calc_distance(row['x'], row['y'], s['x'], s['y']) for s in selected]),
            axis=1
        )
        
        far_enough = candidates_df[candidates_df['min_dist'] > 15].copy()
        
        if len(far_enough) > 0:
            # 選擇最高變異（波動性）
            best_volatile = far_enough.nlargest(1, 'cv').iloc[0]
            grid3 = {
                'x': best_volatile['x'],
                'y': best_volatile['y'],
                'feature': '最高波動性',
                'reason': f'變異係數最高 (CV={best_volatile["cv"]:.2f})',
                **best_volatile.to_dict()
            }
            selected.append(grid3)
            print(f"  ✅ 選擇 #3: 最高波動性 ({grid3['x']:.0f}, {grid3['y']:.0f}) - {grid3['reason']}")
        else:
            print(f"  ⚠️ 沒有更多距離 > 15 的候選，從距離 > 10 中選擇...")
            far_enough = candidates_df[candidates_df['min_dist'] > 10].copy()
            if len(far_enough) > 0:
                best = far_enough.iloc[0]
                grid3 = {
                    'x': best['x'],
                    'y': best['y'],
                    'feature': '地理多樣性',
                    'reason': f'遠離核心區（距離{best["min_dist"]:.1f}）',
                    **best.to_dict()
                }
                selected.append(grid3)
                print(f"  ✅ 選擇 #3: 地理多樣性 ({grid3['x']:.0f}, {grid3['y']:.0f})")
    else:
        print(f"  ⚠️ 沒有距離 > 15 的候選，從所有網格中選擇最遠的...")
        furthest = candidates_df.nlargest(2, 'min_dist')
        for idx, row in furthest.iterrows():
            if len(selected) >= 3:
                break
            grid = {
                'x': row['x'],
                'y': row['y'],
                'feature': f'遠離核心區',
                'reason': f'距離已選網格 {row["min_dist"]:.1f} 單位',
                **row.to_dict()
            }
            selected.append(grid)
            print(f"  ✅ 選擇 #{len(selected)}: ({grid['x']:.0f}, {grid['y']:.0f}) - 距離 {row['min_dist']:.1f}")
    
    return selected

def visualize_selection(features_df, selected):
    """視覺化選擇結果"""
    
    fig = plt.figure(figsize=(18, 6))
    
    # 1. 空間分布
    ax1 = plt.subplot(131)
    
    # 所有網格（按人流量著色）
    scatter = ax1.scatter(features_df['x'], features_df['y'], 
                         s=20, c=features_df['total_flow'], 
                         cmap='YlOrRd', alpha=0.4, vmin=0, vmax=features_df['total_flow'].quantile(0.95))
    plt.colorbar(scatter, ax=ax1, label='總人流')
    
    # 選中的三個
    colors = ['gold', 'lime', 'cyan']
    markers = ['*', 's', 'D']
    
    for idx, grid in enumerate(selected):
        ax1.scatter(grid['x'], grid['y'], s=1000, marker=markers[idx],
                   c=colors[idx], edgecolors='black', linewidths=3,
                   label=f"#{idx+1}: {grid['feature']}", zorder=10)
        
        ax1.annotate(f"#{idx+1}\n{grid['feature']}\n({grid['x']:.0f},{grid['y']:.0f})",
                    xy=(grid['x'], grid['y']), xytext=(20, 20),
                    textcoords='offset points', fontsize=9, fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor=colors[idx], alpha=0.9),
                    arrowprops=dict(arrowstyle='->', lw=2.5))
    
    ax1.set_xlabel('X 座標', fontsize=12)
    ax1.set_ylabel('Y 座標', fontsize=12)
    ax1.set_title('最終選擇的三個網格 - 空間分布', fontsize=13, fontweight='bold')
    ax1.legend(loc='best', fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # 2. 特徵對比（柱狀圖）
    ax2 = plt.subplot(132)
    
    categories = ['總人流\n(萬)', '平均\n人流', '最大\n峰值', '最大\n增幅', '最大\n減幅']
    
    x = np.arange(len(categories))
    width = 0.25
    
    for idx, grid in enumerate(selected):
        values = [
            grid['total_flow'] / 10000,
            grid['mean'],
            grid['max_peak'],
            grid['max_increase'],
            grid['max_decrease']
        ]
        
        ax2.bar(x + idx * width, values, width, label=f"#{idx+1}: {grid['feature']}", 
               color=colors[idx], alpha=0.8, edgecolor='black', linewidth=1.5)
    
    ax2.set_xticks(x + width)
    ax2.set_xticklabels(categories, fontsize=10)
    ax2.set_ylabel('數值', fontsize=12)
    ax2.set_title('三個網格特徵對比', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # 3. 距離矩陣
    ax3 = plt.subplot(133)
    
    dist_matrix = np.zeros((3, 3))
    for i in range(3):
        for j in range(3):
            if i != j:
                dist = np.sqrt((selected[i]['x'] - selected[j]['x'])**2 + 
                             (selected[i]['y'] - selected[j]['y'])**2)
                dist_matrix[i, j] = dist
    
    im = ax3.imshow(dist_matrix, cmap='Greens', vmin=0)
    plt.colorbar(im, ax=ax3, label='距離（單位）')
    
    labels = [f"#{i+1}\n{s['feature']}" for i, s in enumerate(selected)]
    ax3.set_xticks(range(3))
    ax3.set_yticks(range(3))
    ax3.set_xticklabels(labels, fontsize=9)
    ax3.set_yticklabels(labels, fontsize=9)
    
    for i in range(3):
        for j in range(3):
            if i != j:
                ax3.text(j, i, f'{dist_matrix[i, j]:.1f}',
                        ha='center', va='center', fontsize=11, fontweight='bold')
    
    ax3.set_title('網格間距離矩陣', fontsize=13, fontweight='bold')
    
    plt.tight_layout()
    return fig

def main():
    print("="*80)
    print("基於明確特徵指標的網格選擇")
    print("="*80)
    print()
    
    # 計算特徵
    features_df = calculate_grid_features()
    
    # 找出特徵網格
    characteristic_grids = find_characteristic_grids(features_df)
    
    # 選擇最終三個
    selected = select_final_three(characteristic_grids, features_df)
    
    if len(selected) < 3:
        print(f"\n⚠️ 只找到 {len(selected)} 個符合條件的網格")
        print("無法繼續視覺化，但已儲存找到的網格資訊")
        
        # 儲存已選的
        output = {
            'selected_grids': [
                {
                    'rank': idx + 1,
                    'x': int(grid['x']),
                    'y': int(grid['y']),
                    'feature': grid['feature'],
                    'reason': grid['reason'],
                    'total_flow': int(grid['total_flow'])
                }
                for idx, grid in enumerate(selected)
            ]
        }
        
        with open('results/final_selected_grids.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print("\n✓ 結果已儲存: results/final_selected_grids.json")
        return
    
    # 視覺化
    fig = visualize_selection(features_df, selected)
    fig.savefig('results/final_grid_selection.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    
    print(f"\n{'='*80}")
    print("✅ 最終選擇完成")
    print(f"{'='*80}\n")
    
    print("選中的三個網格:")
    for idx, grid in enumerate(selected):
        print(f"\n選擇 #{idx+1}: ({grid['x']:.0f}, {grid['y']:.0f})")
        print(f"  特徵: {grid['feature']}")
        print(f"  理由: {grid['reason']}")
        print(f"  總人流: {grid['total_flow']:,.0f}")
        print(f"  平均: {grid['mean']:.1f}, 最大峰值: {grid['max_peak']:.0f}")
    
    # 距離
    print(f"\n網格間距離:")
    for i in range(len(selected)):
        for j in range(i+1, len(selected)):
            dist = np.sqrt((selected[i]['x'] - selected[j]['x'])**2 + 
                          (selected[i]['y'] - selected[j]['y'])**2)
            print(f"  #{i+1} ↔ #{j+1}: {dist:.1f} 單位")
    
    # 儲存
    output = {
        'selected_grids': [
            {
                'rank': idx + 1,
                'x': int(grid['x']),
                'y': int(grid['y']),
                'feature': grid['feature'],
                'reason': grid['reason'],
                'total_flow': int(grid['total_flow']),
                'mean': float(grid['mean']),
                'max_peak': float(grid['max_peak']),
                'max_increase': float(grid['max_increase']),
                'max_decrease': float(grid['max_decrease'])
            }
            for idx, grid in enumerate(selected)
        ]
    }
    
    with open('results/final_selected_grids.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print("\n✓ 結果已儲存:")
    print("  - results/final_grid_selection.png")
    print("  - results/final_selected_grids.json")

if __name__ == '__main__':
    main()
