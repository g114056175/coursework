"""
最後步驟：創建網格2時序圖並更新選擇理由熱圖
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def create_grid2_timeseries():
    """創建網格2的時序圖"""
    
    df = pd.read_csv('data1.csv')
    
    x, y = 80, 93
    
    grid_data = df[(df['x'] == x) & (df['y'] == y)].copy()
    grid_data = grid_data.sort_values(['d', 't'])
    
    n = grid_data['n'].values
    mean_val = n.mean()
    std_val = n.std()
    cv = std_val / mean_val if mean_val > 0 else 0
    max_val = n.max()
    
    threshold_1sigma = mean_val + 1.0 * std_val
    threshold_15sigma = mean_val + 1.5 * std_val
    
    burst_15 = n > threshold_15sigma
    burst_count = burst_15.sum()
    
    changes = np.diff(n)
    max_increase = changes.max() if len(changes) > 0 else 0
    max_decrease = changes.min() if len(changes) > 0 else 0
    
    time_index = np.arange(len(n))
    train_test_split = 60 * 48
    
    # 繪圖
    fig, ax = plt.subplots(figsize=(20, 8))
    
    ax.plot(time_index, n, color='steelblue', linewidth=1.5, alpha=0.8, label='實際人流')
    
    ax.axhline(y=mean_val, color='green', linestyle='--', linewidth=2, 
              label=f'平均值 ({mean_val:.2f})', alpha=0.7)
    
    ax.axhline(y=threshold_1sigma, color='orange', linestyle=':', linewidth=2.5,
              label=f'1.0σ 門檻 ({threshold_1sigma:.2f})', alpha=0.7)
    ax.axhline(y=threshold_15sigma, color='red', linestyle=':', linewidth=2.5,
              label=f'1.5σ 門檻 ({threshold_15sigma:.2f})', alpha=0.7)
    
    if burst_count > 0:
        ax.scatter(time_index[burst_15], n[burst_15], color='red', s=50, 
                  zorder=5, alpha=0.6, label=f'爆量事件 ({burst_count}次)')
    
    max_idx = n.argmax()
    ax.scatter(max_idx, max_val, color='gold', s=300, marker='*',
              edgecolors='black', linewidths=2, zorder=10,
              label=f'峰值 ({max_val:.0f})')
    
    if train_test_split < len(n):
        ax.axvline(x=train_test_split, color='purple', linestyle='-', linewidth=3,
                  alpha=0.5, label='訓練/測試分割 (60天)')
    
    main_title = f'網格 (80, 93) - 第二高人流\n'
    main_title += f'75天時序數據 (總人流: {n.sum():,}, 平均: {mean_val:.2f}, 標準差: {std_val:.2f}, CV: {cv:.2f})'
    ax.set_title(main_title, fontsize=16, fontweight='bold', pad=20)
    
    ax.set_xlabel('時段索引（0.5小時）', fontsize=13)
    ax.set_ylabel('人數', fontsize=13)
    
    ax.legend(loc='upper right', fontsize=11, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    stats_text = f'數據點: {len(n)}\n'
    stats_text += f'最大增幅: +{max_increase:.0f}\n'
    stats_text += f'最大減幅: {max_decrease:.0f}\n'
    stats_text += f'爆量比例: {burst_count/len(n)*100:.1f}%'
    
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
            fontsize=11, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    
    output_path = 'grid_selection/grid_2_80_93_第二高人流.png'
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    
    print(f"✓ 已儲存: {output_path}")

def update_selection_heatmaps():
    """更新選擇理由熱圖（使用正確的網格）"""
    
    df = pd.read_csv('data1.csv')
    
    print("計算所有網格特徵...")
    grid_features = []
    
    for (x, y), group in df.groupby(['x', 'y']):
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
    
    # 最終網格選擇
    grids = [
        {'rank': 1, 'x': 80, 'y': 95, 'feature': '最高人流', 'metric': 'total_flow'},
        {'rank': 2, 'x': 80, 'y': 93, 'feature': '第二高人流', 'metric': 'total_flow'},
        {'rank': 3, 'x': 79, 'y': 97, 'feature': '最大瞬間湧入', 'metric': 'max_increase'}
    ]
    
    print("更新選擇理由熱圖...")
    
    for grid_info in grids:
        rank = grid_info['rank']
        x, y = grid_info['x'], grid_info['y']
        feature = grid_info['feature']
        metric = grid_info['metric']
        
        # 創建2D網格
        x_range = features_df['x'].unique()
        y_range = features_df['y'].unique()
        
        x_min, x_max = x_range.min(), x_range.max()
        y_min, y_max = y_range.min(), y_range.max()
        
        grid_matrix = np.zeros((int(y_max - y_min + 1), int(x_max - x_min + 1)))
        grid_matrix[:] = np.nan
        
        for _, row in features_df.iterrows():
            xi = int(row['x'] - x_min)
            yi = int(row['y'] - y_min)
            grid_matrix[yi, xi] = row[metric]
        
        # 繪圖
        fig, ax = plt.subplots(figsize=(16, 12))
        
        if metric == 'total_flow':
            cmap = 'YlOrRd'
            label = '累積人流'
        else:  # max_increase
            cmap = 'Reds'
            label = '最大單時段增幅（人）'
        
        im = ax.imshow(grid_matrix, cmap=cmap, aspect='auto', origin='lower',
                      extent=[x_min, x_max, y_min, y_max])
        
        cbar = plt.colorbar(im, ax=ax, label=label, fraction=0.046, pad=0.04)
        cbar.ax.tick_params(labelsize=11)
        
        # 標記選中的網格 - 使用空心圓圈
        circle_size = 800
        ax.scatter(x, y, s=circle_size, marker='o', facecolors='none',
                  edgecolors='blue', linewidths=4, zorder=10,
                  label=f'選中網格: ({x}, {y})')
        
        # 獲取網格數值
        grid_value = features_df[(features_df['x'] == x) & (features_df['y'] == y)][metric].values[0]
        
        # 添加排名資訊
        if metric == 'total_flow':
            rank_num = (features_df['total_flow'] > grid_value).sum() + 1
            text = f'網格 ({x}, {y})\n累積人流: {grid_value:,.0f}\n排名第{rank_num}'
        else:
            rank_num = (features_df['max_increase'] > grid_value).sum() + 1
            text = f'網格 ({x}, {y})\n最大增幅: +{grid_value:.0f}人\n排名第{rank_num}'
        
        bbox_props = dict(boxstyle='round,pad=0.8', facecolor='blue', 
                         edgecolor='white', linewidth=3, alpha=0.95)
        
        ax.annotate(text, xy=(x, y), xytext=(50, 50), 
                   textcoords='offset points', fontsize=13, fontweight='bold',
                   color='white', bbox=bbox_props,
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.3',
                                 color='white', lw=3.5), zorder=11)
        
        title = f'網格選擇理由 #{rank}: {feature}\n'
        title += f'選擇標準: {label}'
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        ax.set_xlabel('X 座標', fontsize=13)
        ax.set_ylabel('Y 座標', fontsize=13)
        ax.legend(loc='upper left', fontsize=12, framealpha=0.9)
        ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.5)
        
        plt.tight_layout()
        
        output_file = f'grid_selection/selection_justification_{rank}_{feature}.png'
        fig.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close(fig)
        
        print(f"  ✓ {feature}: 排名第{rank_num}")

def main():
    print("="*80)
    print("最後步驟：創建時序圖與更新選擇理由熱圖")
    print("="*80)
    print()
    
    print("1. 創建網格2時序圖...")
    create_grid2_timeseries()
    
    print("\n2. 更新選擇理由熱圖...")
    update_selection_heatmaps()
    
    print("\n" + "="*80)
    print("✅ 所有工作完成！")
    print("="*80)

if __name__ == '__main__':
    main()
