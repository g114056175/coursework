"""
網格人流空間分布分析

1. 計算每個網格 75 天的累積人流
2. 繪製空間熱圖
3. 標記 Top 5 人流最多的網格
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json

plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def analyze_spatial_distribution():
    """分析網格空間分布"""
    
    print("讀取數據...")
    df = pd.read_csv('data1.csv')
    
    print(f"數據形狀: {df.shape}")
    print(f"時間範圍: {df['d'].min()} - {df['d'].max()} 天")
    print(f"網格範圍: X: {df['x'].min()}-{df['x'].max()}, Y: {df['y'].min()}-{df['y'].max()}")
    
    # 計算每個網格的累積人流
    print("\n計算每個網格的累積人流...")
    grid_total = df.groupby(['x', 'y'])['n'].sum().reset_index()
    grid_total.columns = ['x', 'y', 'total_flow']
    
    # 排序找出 Top 5
    top_5 = grid_total.nlargest(5, 'total_flow')
    
    print(f"\n{'='*70}")
    print("Top 5 累積人流最多的網格")
    print(f"{'='*70}")
    print(f"{'排名':<6} {'座標 (x, y)':<20} {'累積人流':<15} {'佔比':<10}")
    print("-"*70)
    
    total_all = grid_total['total_flow'].sum()
    
    for idx, row in top_5.iterrows():
        rank = top_5.index.get_loc(idx) + 1
        percentage = row['total_flow'] / total_all * 100
        print(f"{rank:<6} ({row['x']:.0f}, {row['y']:.0f}){'':<12} {row['total_flow']:.0f}{'':<6} {percentage:.2f}%")
    
    return grid_total, top_5

def create_heatmap(grid_total, top_5):
    """繪製空間熱圖"""
    
    print(f"\n繪製空間熱圖...")
    
    # 建立網格矩陣
    x_min, x_max = int(grid_total['x'].min()), int(grid_total['x'].max())
    y_min, y_max = int(grid_total['y'].min()), int(grid_total['y'].max())
    
    # 建立空矩陣
    matrix = np.zeros((y_max - y_min + 1, x_max - x_min + 1))
    
    # 填充數據
    for _, row in grid_total.iterrows():
        x_idx = int(row['x']) - x_min
        y_idx = int(row['y']) - y_min
        matrix[y_idx, x_idx] = row['total_flow']
    
    # 繪圖
    fig, ax = plt.subplots(figsize=(16, 12))
    
    # 熱圖
    im = ax.imshow(matrix, cmap='YlOrRd', aspect='auto', origin='lower',
                   extent=[x_min, x_max, y_min, y_max])
    
    # 色標
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('累積人流（75天總和）', fontsize=12, rotation=270, labelpad=20)
    
    # 標記 Top 5 - 使用不同的偏移方向避免重疊
    offsets = [
        (40, 40),   # 右上
        (-100, 40),  # 左上
        (40, -40),  # 右下
        (-100, -40), # 左下
        (0, 60)     # 正上
    ]
    
    for idx, row in top_5.iterrows():
        rank = top_5.index.get_loc(idx) + 1
        x, y = row['x'], row['y']
        offset = offsets[rank - 1]
        
        # 大星星標記
        ax.scatter(x, y, s=1000, marker='*', color='blue', 
                  edgecolors='white', linewidths=3, zorder=10)
        
        # 標註
        ax.annotate(f'#{rank}\n({x:.0f}, {y:.0f})\n{row["total_flow"]/1000:.0f}K', 
                   xy=(x, y), xytext=offset, textcoords='offset points',
                   fontsize=11, fontweight='bold', color='white',
                   bbox=dict(boxstyle='round,pad=0.6', facecolor='blue', 
                           edgecolor='white', linewidth=2, alpha=0.9),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.3', 
                                 color='white', lw=2.5),
                   zorder=11)
    
    ax.set_xlabel('X 座標', fontsize=14)
    ax.set_ylabel('Y 座標', fontsize=14)
    ax.set_title('網格累積人流空間分布（75天）- Top 5 標記', 
                fontsize=16, fontweight='bold', pad=20)
    
    # 網格線
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    
    plt.tight_layout()
    return fig

def create_top5_details(top_5):
    """建立 Top 5 詳細分析圖"""
    
    print("分析 Top 5 網格的時間序列特徵...")
    
    df = pd.read_csv('data1.csv')
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()
    
    for idx, row in top_5.iterrows():
        rank = top_5.index.get_loc(idx) + 1
        x, y = int(row['x']), int(row['y'])
        
        # 提取該網格數據
        grid_data = df[(df['x'] == x) & (df['y'] == y)].copy()
        grid_data = grid_data.sort_values(['d', 't'])
        
        ax = axes[rank - 1]
        
        # 時間序列
        time_index = np.arange(len(grid_data))
        ax.plot(time_index, grid_data['n'].values, linewidth=1, alpha=0.7, color='steelblue')
        
        # 統計
        mean_val = grid_data['n'].mean()
        std_val = grid_data['n'].std()
        max_val = grid_data['n'].max()
        
        ax.axhline(y=mean_val, color='red', linestyle='--', alpha=0.7, label=f'平均 ({mean_val:.1f})')
        ax.axhline(y=mean_val + 1.5*std_val, color='orange', linestyle=':', alpha=0.7, 
                  label=f'門檻 ({mean_val + 1.5*std_val:.1f})')
        
        ax.set_title(f'#{rank}: 網格 ({x}, {y})\n累積: {row["total_flow"]/1000:.1f}K, Max: {max_val:.0f}',
                    fontsize=11, fontweight='bold')
        ax.set_xlabel('時間索引', fontsize=9)
        ax.set_ylabel('人數', fontsize=9)
        ax.legend(fontsize=8, loc='upper right')
        ax.grid(True, alpha=0.3)
    
    # 隱藏第6個子圖
    axes[5].axis('off')
    
    plt.suptitle('Top 5 網格時間序列分析', fontsize=16, fontweight='bold')
    plt.tight_layout()
    return fig

def save_top5_info(top_5):
    """儲存 Top 5 資訊"""
    
    top5_list = []
    for idx, row in top_5.iterrows():
        rank = top_5.index.get_loc(idx) + 1
        top5_list.append({
            'rank': rank,
            'x': int(row['x']),
            'y': int(row['y']),
            'total_flow': int(row['total_flow'])
        })
    
    output = {
        'top_grids': top5_list,
        'analysis_date': '2024-12-15',
        'threshold_type': 'cumulative_flow_top5'
    }
    
    with open('results/top5_grids_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Top 5 資訊已儲存: results/top5_grids_analysis.json")

def main():
    print("="*70)
    print("網格人流空間分布分析")
    print("="*70)
    print()
    
    # 分析
    grid_total, top_5 = analyze_spatial_distribution()
    
    # 熱圖
    fig1 = create_heatmap(grid_total, top_5)
    fig1.savefig('results/spatial_heatmap_top5.png', dpi=150, bbox_inches='tight')
    plt.close(fig1)
    print("✓ 空間熱圖已儲存: results/spatial_heatmap_top5.png")
    
    # Top 5 詳細分析
    fig2 = create_top5_details(top_5)
    fig2.savefig('results/top5_timeseries_analysis.png', dpi=150, bbox_inches='tight')
    plt.close(fig2)
    print("✓ Top 5 時間序列已儲存: results/top5_timeseries_analysis.png")
    
    # 儲存資訊
    save_top5_info(top_5)
    
    print(f"\n{'='*70}")
    print("✅ 分析完成！")
    print("\n產生的檔案：")
    print("  1. results/spatial_heatmap_top5.png - 空間分布熱圖（標記 Top 5）")
    print("  2. results/top5_timeseries_analysis.png - Top 5 時間序列分析")
    print("  3. results/top5_grids_analysis.json - Top 5 網格資訊")

if __name__ == '__main__':
    main()
