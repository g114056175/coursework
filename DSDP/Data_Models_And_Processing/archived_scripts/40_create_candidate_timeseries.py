"""
為網格 (79, 97) 和 (89, 79) 創建時序折線圖

放置於 grid_selection 資料夾
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def create_timeseries_plot(df, x, y, title, filename):
    """創建時序折線圖"""
    
    # 提取網格數據
    grid_data = df[(df['x'] == x) & (df['y'] == y)].copy()
    grid_data = grid_data.sort_values(['d', 't'])
    
    n = grid_data['n'].values
    
    if len(n) == 0:
        print(f"  ❌ 網格 ({x}, {y}) 無數據")
        return
    
    # 統計
    mean_val = n.mean()
    std_val = n.std()
    cv = std_val / mean_val if mean_val > 0 else 0
    max_val = n.max()
    
    # 計算門檻
    threshold_1sigma = mean_val + 1.0 * std_val
    threshold_15sigma = mean_val + 1.5 * std_val
    
    # 爆量事件
    burst_15 = n > threshold_15sigma
    burst_count = burst_15.sum()
    
    # 最大變化
    changes = np.diff(n)
    max_increase = changes.max() if len(changes) > 0 else 0
    max_decrease = changes.min() if len(changes) > 0 else 0
    
    # 時間索引
    time_index = np.arange(len(n))
    
    # 訓練/測試分割點（60天）
    train_test_split = 60 * 48
    
    # 繪圖
    fig, ax = plt.subplots(figsize=(20, 8))
    
    # 主要折線
    ax.plot(time_index, n, color='steelblue', linewidth=1.5, alpha=0.8, label='實際人流')
    
    # 平均線
    ax.axhline(y=mean_val, color='green', linestyle='--', linewidth=2, 
              label=f'平均值 ({mean_val:.2f})', alpha=0.7)
    
    # 門檻線
    ax.axhline(y=threshold_1sigma, color='orange', linestyle=':', linewidth=2.5,
              label=f'1.0σ 門檻 ({threshold_1sigma:.2f})', alpha=0.7)
    ax.axhline(y=threshold_15sigma, color='red', linestyle=':', linewidth=2.5,
              label=f'1.5σ 門檻 ({threshold_15sigma:.2f})', alpha=0.7)
    
    # 標記爆量點（1.5σ）
    if burst_count > 0:
        ax.scatter(time_index[burst_15], n[burst_15], color='red', s=50, 
                  zorder=5, alpha=0.6, label=f'爆量事件 ({burst_count}次)')
    
    # 標記峰值
    max_idx = n.argmax()
    ax.scatter(max_idx, max_val, color='gold', s=300, marker='*',
              edgecolors='black', linewidths=2, zorder=10,
              label=f'峰值 ({max_val:.0f})')
    
    # 訓練/測試分割線
    if train_test_split < len(n):
        ax.axvline(x=train_test_split, color='purple', linestyle='-', linewidth=3,
                  alpha=0.5, label='訓練/測試分割 (60天)')
    
    # 標題和標籤
    main_title = f'{title}\n'
    main_title += f'75天時序數據 (總人流: {n.sum():,}, 平均: {mean_val:.2f}, 標準差: {std_val:.2f}, CV: {cv:.2f})'
    ax.set_title(main_title, fontsize=16, fontweight='bold', pad=20)
    
    ax.set_xlabel('時段索引（0.5小時）', fontsize=13)
    ax.set_ylabel('人數', fontsize=13)
    
    # 圖例
    ax.legend(loc='upper right', fontsize=11, framealpha=0.9)
    
    # 網格
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # 統計資訊文字框
    stats_text = f'數據點: {len(n)}\n'
    stats_text += f'最大增幅: +{max_increase:.0f}\n'
    stats_text += f'最大減幅: {max_decrease:.0f}\n'
    stats_text += f'爆量比例: {burst_count/len(n)*100:.1f}%'
    
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
            fontsize=11, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    
    # 儲存
    output_path = f'grid_selection/{filename}'
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    
    print(f"  ✓ 已儲存: {output_path}")
    print(f"    總人流: {n.sum():,}, 平均: {mean_val:.2f}, CV: {cv:.2f}, 最大增幅: +{max_increase:.0f}")

def main():
    print("="*80)
    print("創建網格 (79, 97) 和 (89, 79) 的時序折線圖")
    print("="*80)
    print()
    
    df = pd.read_csv('data1.csv')
    
    grids = [
        {
            'x': 79,
            'y': 97,
            'title': '網格 (79, 97) - 最大瞬間湧入',
            'filename': 'grid_79_97_最大瞬間湧入.png'
        },
        {
            'x': 89,
            'y': 79,
            'title': '網格 (89, 79) - 最高波動性',
            'filename': 'grid_89_79_最高波動性.png'
        }
    ]
    
    for grid in grids:
        print(f"處理網格 ({grid['x']}, {grid['y']})...")
        create_timeseries_plot(df, grid['x'], grid['y'], grid['title'], grid['filename'])
        print()
    
    print("="*80)
    print("✅ 完成！")
    print("="*80)

if __name__ == '__main__':
    main()
