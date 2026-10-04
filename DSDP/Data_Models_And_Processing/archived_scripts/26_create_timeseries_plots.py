"""
為最終選擇的三個網格創建時序折線圖
儲存在 temp 資料夾中
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import os

plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def create_timeseries_plots():
    """為三個選定網格創建時序圖"""
    
    # 創建 temp 資料夾
    os.makedirs('temp', exist_ok=True)
    print("已創建 temp 資料夾\n")
    
    # 載入選定網格
    with open('results/final_selected_grids.json', 'r', encoding='utf-8') as f:
        selected_data = json.load(f)
    
    selected_grids = selected_data['selected_grids']
    
    # 讀取數據
    df = pd.read_csv('data1.csv')
    
    for grid_info in selected_grids:
        rank = grid_info['rank']
        x, y = grid_info['x'], grid_info['y']
        feature = grid_info['feature']
        reason = grid_info['reason']
        
        print(f"處理網格 #{rank}: ({x}, {y}) - {feature}")
        
        # 提取該網格數據
        grid_data = df[(df['x'] == x) & (df['y'] == y)].copy()
        grid_data = grid_data.sort_values(['d', 't'])
        
        n = grid_data['n'].values
        time_index = np.arange(len(n))
        
        # 統計
        mean_val = n.mean()
        std_val = n.std()
        max_val = n.max()
        min_val = n.min()
        
        # 門檻
        threshold_10 = mean_val + 1.0 * std_val
        threshold_15 = mean_val + 1.5 * std_val
        
        # 爆量時刻
        burst_10 = n > threshold_10
        burst_15 = n > threshold_15
        
        # 繪圖
        fig, ax = plt.subplots(figsize=(20, 6))
        
        # 主折線
        ax.plot(time_index, n, linewidth=1.5, alpha=0.8, color='steelblue', label='人流數')
        
        # 平均線
        ax.axhline(y=mean_val, color='green', linestyle='--', linewidth=2, 
                  label=f'平均值 ({mean_val:.1f})', alpha=0.7)
        
        # 門檻線
        ax.axhline(y=threshold_10, color='orange', linestyle=':', linewidth=2, 
                  label=f'1.0σ 門檻 ({threshold_10:.1f})', alpha=0.7)
        ax.axhline(y=threshold_15, color='red', linestyle=':', linewidth=2, 
                  label=f'1.5σ 門檻 ({threshold_15:.1f})', alpha=0.7)
        
        # 標記爆量點（1.5σ）
        if burst_15.sum() > 0:
            ax.scatter(time_index[burst_15], n[burst_15], 
                      color='red', s=30, alpha=0.6, label=f'1.5σ 爆量點 ({burst_15.sum()})', zorder=5)
        
        # 標記峰值
        max_idx = n.argmax()
        ax.scatter(max_idx, max_val, s=200, marker='*', color='gold', 
                  edgecolors='black', linewidths=2, label=f'峰值 ({max_val:.0f})', zorder=10)
        
        # 訓練/測試分割線（60天）
        split_point = 60 * 48
        ax.axvline(x=split_point, color='purple', linestyle='--', linewidth=2.5, 
                  label='訓練/測試分割', alpha=0.6)
        
        # 標題和標籤
        title = f'網格 #{rank}: ({x}, {y}) - {feature}\n'
        title += f'{reason}\n'
        title += f'平均: {mean_val:.1f}, 標準差: {std_val:.1f}, 峰值: {max_val:.0f}, CV: {std_val/mean_val:.2f}'
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('時間索引（時段，每天48個時段，共75天）', fontsize=12)
        ax.set_ylabel('人數', fontsize=12)
        
        # 圖例
        ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
        
        # 網格
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # X軸刻度（標示天數）
        day_ticks = np.arange(0, len(n), 48)
        day_labels = [f'D{i}' for i in range(len(day_ticks))]
        ax.set_xticks(day_ticks[::5])  # 每5天一個刻度
        ax.set_xticklabels(day_labels[::5], rotation=45)
        
        # 設定 Y 軸範圍
        ax.set_ylim([max(0, min_val - 5), max_val * 1.1])
        
        plt.tight_layout()
        
        # 儲存
        filename = f'temp/grid_{rank}_{x}_{y}_{feature}.png'
        fig.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close(fig)
        
        print(f"  ✓ 已儲存: {filename}\n")
    
    # 創建一個合併比較圖
    print("創建三網格比較圖...")
    fig, axes = plt.subplots(3, 1, figsize=(20, 12))
    
    for idx, grid_info in enumerate(selected_grids):
        rank = grid_info['rank']
        x, y = grid_info['x'], grid_info['y']
        feature = grid_info['feature']
        
        # 提取數據
        grid_data = df[(df['x'] == x) & (df['y'] == y)].copy()
        grid_data = grid_data.sort_values(['d', 't'])
        n = grid_data['n'].values
        time_index = np.arange(len(n))
        
        ax = axes[idx]
        
        # 繪製
        ax.plot(time_index, n, linewidth=1.5, alpha=0.8, color='steelblue')
        
        mean_val = n.mean()
        threshold = mean_val + 1.0 * n.std()
        
        ax.axhline(y=mean_val, color='green', linestyle='--', linewidth=2, alpha=0.7)
        ax.axhline(y=threshold, color='red', linestyle=':', linewidth=2, alpha=0.7)
        ax.axvline(x=60*48, color='purple', linestyle='--', linewidth=2, alpha=0.6)
        
        ax.set_title(f'#{rank}: ({x}, {y}) - {feature}', fontsize=13, fontweight='bold')
        ax.set_ylabel('人數', fontsize=11)
        ax.grid(True, alpha=0.3)
        
        if idx == 2:
            ax.set_xlabel('時間索引', fontsize=11)
    
    plt.suptitle('三個網格時序對比', fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    comparison_file = 'temp/comparison_all_grids.png'
    fig.savefig(comparison_file, dpi=150, bbox_inches='tight')
    plt.close(fig)
    
    print(f"  ✓ 已儲存: {comparison_file}\n")

def main():
    print("="*70)
    print("為選定網格創建時序折線圖")
    print("="*70)
    print()
    
    create_timeseries_plots()
    
    print("="*70)
    print("✅ 完成！所有圖表已儲存在 temp 資料夾中")
    print("="*70)
    print("\n產生的檔案：")
    print("  1. temp/grid_1_80_95_最高人流.png")
    print("  2. temp/grid_2_34_44_最大瞬間湧入.png")
    print("  3. temp/grid_3_86_149_最高波動性.png")
    print("  4. temp/comparison_all_grids.png - 三網格對比")

if __name__ == '__main__':
    main()
