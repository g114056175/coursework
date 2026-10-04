"""
創建累積人數熱圖並標記前3高的網格
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def create_top3_heatmap():
    print("="*80)
    print("創建累積人數熱圖（標記前3高網格）")
    print("="*80)
    print()
    
    df = pd.read_csv('data1.csv')
    
    # 計算每個網格的累積人流
    grid_total = df.groupby(['x', 'y'])['n'].sum().reset_index()
    grid_total.columns = ['x', 'y', 'total_flow']
    
    print(f"總網格數: {len(grid_total)}")
    
    # 找出前3名
    top_3 = grid_total.nlargest(3, 'total_flow')
    
    print("\nTop 3 網格:")
    for idx, (_, row) in enumerate(top_3.iterrows(), 1):
        print(f"  {idx}. ({row['x']:.0f}, {row['y']:.0f}): {row['total_flow']:,.0f}")
    
    # 創建2D矩陣
    x_range = grid_total['x'].unique()
    y_range = grid_total['y'].unique()
    
    x_min, x_max = x_range.min(), x_range.max()
    y_min, y_max = y_range.min(), y_range.max()
    
    # 創建空矩陣
    grid_matrix = np.zeros((int(y_max - y_min + 1), int(x_max - x_min + 1)))
    grid_matrix[:] = np.nan
    
    # 填充數據
    for _, row in grid_total.iterrows():
        xi = int(row['x'] - x_min)
        yi = int(row['y'] - y_min)
        grid_matrix[yi, xi] = row['total_flow']
    
    # 繪製熱圖
    fig, ax = plt.subplots(figsize=(20, 16))
    
    # 熱圖
    im = ax.imshow(grid_matrix, cmap='YlOrRd', aspect='auto', origin='lower',
                   extent=[x_min, x_max, y_min, y_max], interpolation='nearest')
    
    # 色彩條
    cbar = plt.colorbar(im, ax=ax, label='累積人流', fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=12)
    
    # 標記前3名網格
    colors = ['blue', 'green', 'purple']
    markers = ['o', 's', '^']  # 圓形、方形、三角形
    
    for idx, (_, row) in enumerate(top_3.iterrows()):
        x, y = row['x'], row['y']
        total = row['total_flow']
        
        # 繪製標記（空心）
        ax.scatter(x, y, s=1200, marker=markers[idx], facecolors='none',
                  edgecolors=colors[idx], linewidths=5, zorder=10,
                  label=f'第{idx+1}名: ({x:.0f}, {y:.0f})')
        
        # 添加文字標註
        bbox_props = dict(boxstyle='round,pad=0.8', facecolor=colors[idx], 
                         edgecolor='white', linewidth=3, alpha=0.95)
        
        # 計算偏移方向（避免重疊）
        offsets = [(60, 60), (-120, 60), (60, -60)]
        offset = offsets[idx]
        
        text = f'#{idx+1}\n({x:.0f}, {y:.0f})\n{total/1000:.1f}K'
        
        ax.annotate(text, xy=(x, y), xytext=offset, 
                   textcoords='offset points', fontsize=13, fontweight='bold',
                   color='white', bbox=bbox_props,
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.3',
                                 color='white', lw=4), zorder=11)
    
    # 標題
    title = '累積人流空間分布熱圖\n'
    title += f'75天總人流分布（Top 3 高亮標記）'
    ax.set_title(title, fontsize=18, fontweight='bold', pad=20)
    
    ax.set_xlabel('X 座標', fontsize=14)
    ax.set_ylabel('Y 座標', fontsize=14)
    
    # 圖例
    ax.legend(loc='upper left', fontsize=13, framealpha=0.95, 
             edgecolor='black', fancybox=True, shadow=True)
    
    # 網格線
    ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.5, color='black')
    
    # 統計資訊
    stats_text = f'總網格數: {len(grid_total)}\n'
    stats_text += f'最高人流: {grid_total["total_flow"].max():,.0f}\n'
    stats_text += f'平均人流: {grid_total["total_flow"].mean():,.0f}\n'
    stats_text += f'總人流量: {grid_total["total_flow"].sum():,.0f}'
    
    ax.text(0.98, 0.02, stats_text, transform=ax.transAxes,
            fontsize=12, verticalalignment='bottom', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9,
                     edgecolor='black', linewidth=2))
    
    plt.tight_layout()
    
    # 儲存
    output_path = 'grid_selection/spatial_heatmap_top3.png'
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    
    print(f"\n✓ 已儲存: {output_path}")
    print()
    print("="*80)
    print("✅ 完成！")
    print("="*80)

if __name__ == '__main__':
    create_top3_heatmap()
