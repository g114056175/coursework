"""
為三個選定網格創建 Persistence (t-1) Baseline 分析

1. 預測誤差折線圖（預測值 - 真實值）
2. 爆量預測混淆矩陣（使用 1.0σ 門檻）
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from sklearn.metrics import confusion_matrix
import os

plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def create_persistence_baseline_analysis():
    """創建 Persistence baseline 分析"""
    
    # 直接使用選定的三個網格
    selected_grids = [
        {'rank': 1, 'x': 80, 'y': 95, 'feature': '最高人流'},
        {'rank': 2, 'x': 34, 'y': 44, 'feature': '最大瞬間湧入'},
        {'rank': 3, 'x': 86, 'y': 149, 'feature': '最高波動性'}
    ]
    
    # 讀取數據
    df = pd.read_csv('data1.csv')
    
    print("="*80)
    print("Persistence (t-1) Baseline 分析")
    print("="*80)
    print()
    
    # === 1. 預測誤差折線圖 ===
    print("1. 創建預測誤差折線圖...")
    
    fig_errors, axes = plt.subplots(3, 1, figsize=(20, 12))
    
    for idx, grid_info in enumerate(selected_grids):
        rank = grid_info['rank']
        x, y = grid_info['x'], grid_info['y']
        feature = grid_info['feature']
        
        # 提取數據
        grid_data = df[(df['x'] == x) & (df['y'] == y)].copy()
        grid_data = grid_data.sort_values(['d', 't'])
        
        n = grid_data['n'].values
        
        # 測試集（後15天）
        train_size = 60 * 48
        n_test = n[train_size:]
        n_t1_test = n[train_size-1:-1]  # t-1 作為預測
        
        # 預測誤差
        errors = n_t1_test - n_test
        time_index = np.arange(len(errors))
        
        # 統計
        mae = np.mean(np.abs(errors))
        rmse = np.sqrt(np.mean(errors**2))
        mean_error = np.mean(errors)
        
        ax = axes[idx]
        
        # 繪製誤差
        ax.plot(time_index, errors, linewidth=1.2, alpha=0.7, color='steelblue', label='預測誤差 (t-1 - 真實)')
        ax.axhline(y=0, color='black', linestyle='-', linewidth=2, alpha=0.8, label='零誤差線')
        ax.axhline(y=mean_error, color='red', linestyle='--', linewidth=2, alpha=0.7, 
                  label=f'平均誤差 ({mean_error:.2f})')
        
        # 填充區域
        ax.fill_between(time_index, 0, errors, where=(errors >= 0), alpha=0.3, color='green', label='高估')
        ax.fill_between(time_index, 0, errors, where=(errors < 0), alpha=0.3, color='red', label='低估')
        
        # 訓練/測試分割標記（測試集內部不需要，但可以標示15天）
        for day in range(0, 15, 5):
            ax.axvline(x=day*48, color='gray', linestyle=':', alpha=0.3, linewidth=1)
        
        # 標題
        title = f'網格 #{rank}: ({x}, {y}) - {feature}\n'
        title += f'MAE: {mae:.2f}, RMSE: {rmse:.2f}, Mean Error: {mean_error:.2f}'
        ax.set_title(title, fontsize=12, fontweight='bold')
        
        ax.set_ylabel('預測誤差（人數）', fontsize=11)
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3)
        
        if idx == 2:
            ax.set_xlabel('測試集時間索引（時段）', fontsize=11)
        
        print(f"  網格 #{rank}: MAE={mae:.2f}, RMSE={rmse:.2f}, 平均誤差={mean_error:.2f}")
    
    plt.suptitle('Persistence (t-1) Baseline - 預測誤差分析', fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    error_file = 'grid_selection/persistence_errors.png'
    fig_errors.savefig(error_file, dpi=150, bbox_inches='tight')
    plt.close(fig_errors)
    
    print(f"\n  ✓ 已儲存: {error_file}\n")
    
    # === 2. 爆量預測混淆矩陣 ===
    print("2. 創建爆量預測混淆矩陣（1.0σ 門檻）...")
    
    fig_cm, axes_cm = plt.subplots(1, 3, figsize=(18, 5))
    
    for idx, grid_info in enumerate(selected_grids):
        rank = grid_info['rank']
        x, y = grid_info['x'], grid_info['y']
        feature = grid_info['feature']
        
        # 提取數據
        grid_data = df[(df['x'] == x) & (df['y'] == y)].copy()
        grid_data = grid_data.sort_values(['d', 't'])
        
        n = grid_data['n'].values
        
        # 訓練集統計
        train_size = 60 * 48
        n_train = n[:train_size]
        train_mean = n_train.mean()
        train_std = n_train.std()
        
        # 1.0σ 門檻
        threshold = train_mean + 1.0 * train_std
        
        # 測試集
        n_test = n[train_size:]
        n_t1_test = n[train_size-1:-1]
        
        # 真實標籤和預測標籤
        y_true = (n_test > threshold).astype(int)
        y_pred = (n_t1_test > threshold).astype(int)
        
        # 混淆矩陣
        cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel()
        
        # 計算指標
        accuracy = (tp + tn) / (tp + tn + fp + fn)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        # 百分比
        cm_percent = cm.astype('float') / cm.sum() * 100
        
        # 標註
        annot = np.array([[f'{cm[0,0]}\n({cm_percent[0,0]:.1f}%)', 
                          f'{cm[0,1]}\n({cm_percent[0,1]:.1f}%)'],
                         [f'{cm[1,0]}\n({cm_percent[1,0]:.1f}%)', 
                          f'{cm[1,1]}\n({cm_percent[1,1]:.1f}%)']])
        
        ax = axes_cm[idx]
        
        sns.heatmap(cm, annot=annot, fmt='', cmap='Oranges', 
                   xticklabels=['預測: 正常', '預測: 爆量'],
                   yticklabels=['真實: 正常', '真實: 爆量'],
                   ax=ax, cbar=True, linewidths=2, linecolor='white',
                   annot_kws={'fontsize': 11, 'weight': 'bold'})
        
        title = f'網格 #{rank}: ({x}, {y})\n{feature}\n'
        title += f'準確度: {accuracy*100:.1f}% | 召回率: {recall*100:.1f}% | 精確度: {precision*100:.1f}%'
        ax.set_title(title, fontsize=11, fontweight='bold', pad=12)
        
        # 統計資訊
        info_text = f'門檻: {threshold:.1f} (1.0σ)\nTN={tn}, FP={fp}\nFN={fn}, TP={tp}\nF1={f1:.3f}'
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
                fontsize=9, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
        
        print(f"  網格 #{rank}: 準確度={accuracy*100:.1f}%, 召回率={recall*100:.1f}%, 精確度={precision*100:.1f}%")
    
    plt.suptitle('Persistence (t-1) Baseline - 爆量預測混淆矩陣（門檻 = Mean + 1.0σ）', 
                fontsize=15, fontweight='bold', y=1.00)
    plt.tight_layout()
    
    cm_file = 'grid_selection/persistence_confusion_matrix.png'
    fig_cm.savefig(cm_file, dpi=150, bbox_inches='tight')
    plt.close(fig_cm)
    
    print(f"\n  ✓ 已儲存: {cm_file}\n")

def main():
    print("\n開始創建 Persistence Baseline 分析...\n")
    
    create_persistence_baseline_analysis()
    
    print("="*80)
    print("✅ 完成！")
    print("="*80)
    print("\n產生的檔案：")
    print("  1. grid_selection/persistence_errors.png - 預測誤差折線圖")
    print("  2. grid_selection/persistence_confusion_matrix.png - 爆量預測混淆矩陣")

if __name__ == '__main__':
    main()
