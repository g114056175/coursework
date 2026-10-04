"""
為所有3個網格生成評估圖表

生成：
1. 每個網格5張預測對比圖（共15張）
2. 每個網格1張混淆矩陣（共3張）

並清理舊的temp檔案
"""

import torch
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from resnet_models_29 import create_model_variants

plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def load_model_and_predict(model, checkpoint_path, X_test, device):
    checkpoint = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    with torch.no_grad():
        X_tensor = torch.FloatTensor(X_test).to(device)
        predictions = model(X_tensor).cpu().numpy()
    
    return predictions

def create_all_visualizations():
    print("="*80)
    print("清理舊temp檔案並生成新評估圖表")
    print("="*80)
    print()
    
    # 清理temp資料夾
    print("清理 temp 資料夾...")
    for f in os.listdir('temp'):
        if f.endswith('.png'):
            os.remove(f'temp/{f}')
            print(f"  已刪除: {f}")
    
    print()
    
    device = torch.device('cpu')
    
    grids = [
        {'rank': 1, 'x': 80, 'y': 95, 'feature': '最高人流'},
        {'rank': 2, 'x': 80, 'y': 93, 'feature': '第二高人流'},
        {'rank': 3, 'x': 79, 'y': 97, 'feature': '最大瞬間湧入'}
    ]
    
    variant_names = ['baseline', 'deep', 'wide', 'leaky_relu', 'gelu']
    
    for grid_info in grids:
        rank = grid_info['rank']
        x, y = grid_info['x'], grid_info['y']
        feature = grid_info['feature']
        
        print(f"\n{'='*80}")
        print(f"網格 #{rank}: ({x}, {y}) - {feature}")
        print(f"{'='*80}\n")
        
        # 載入數據
        data_file = f'resnet_features/grid_{rank}_{x}_{y}.npz'
        data = np.load(data_file, allow_pickle=True)
        
        X_test = data['X_test']
        y_test = data['y_test']
        burst_threshold = float(data['burst_threshold'])
        
        time_index = np.arange(len(y_test))
        input_dim = X_test.shape[1]
        variants = create_model_variants(input_dim)
        
        #=== 1. 預測對比圖 ===
        print("創建預測對比圖...")
        for variant_name in variant_names:
            variant_info = variants[variant_name]
            model = variant_info['model'].to(device)
            
            checkpoint_path = f'resnet_models/grid{rank}_{variant_name}.pth'
            predictions = load_model_and_predict(model, checkpoint_path, X_test, device)
            
            mae = np.mean(np.abs(predictions - y_test))
            
            # 繪圖
            fig, ax = plt.subplots(figsize=(20, 6))
            
            ax.plot(time_index, y_test, color='black', linewidth=2.5, 
                   label='真實值', alpha=0.8, zorder=3)
            ax.plot(time_index, predictions, color='steelblue', linewidth=2, 
                   label=f'預測值 ({variant_info["name"]})', alpha=0.7, linestyle='--', zorder=2)
            
            ax.axhline(y=burst_threshold, color='red', linestyle=':', linewidth=2.5, 
                      label=f'爆量門檻 (1.0σ = {burst_threshold:.1f})', alpha=0.6, zorder=1)
            
            title = f'網格 #{rank}: ({x}, {y}) - {feature}\n'
            title += f'{variant_info["name"]} - {variant_info["description"]}\n'
            title += f'MAE: {mae:.2f}, 測試集樣本數: {len(y_test)}'
            
            ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
            ax.set_xlabel('測試集時間索引（時段）', fontsize=12)
            ax.set_ylabel('人數', fontsize=12)
            ax.legend(loc='upper right', fontsize=11, framealpha=0.9)
            ax.grid(True, alpha=0.3, linestyle='--')
            
            y_max = max(y_test.max(), predictions.max())
            ax.set_ylim([0, y_max * 1.1])
            
            plt.tight_layout()
            
            output_file = f'temp/grid{rank}_{variant_name}_prediction.png'
            fig.savefig(output_file, dpi=150, bbox_inches='tight')
            plt.close(fig)
            
            print(f"  ✓ {variant_info['name']}: MAE={mae:.2f}")
        
        #=== 2. 混淆矩陣 ===
        print(f"\n創建混淆矩陣...")
        
        y_true_labels = (y_test > burst_threshold).astype(int)
        
        # Persistence baseline
        df = pd.read_csv('data1.csv')
        grid_data = df[(df['x'] == x) & (df['y'] == y)].copy()
        grid_data = grid_data.sort_values(['d', 't'])
        n = grid_data['n'].values
        
        warmup = 336
        train_size = 60 * 48
        total_after_warmup = len(n) - warmup
        
        n_after_warmup = n[warmup:]
        n_t1_test = n_after_warmup[train_size-1:total_after_warmup-1]
        
        y_pred_persistence = (n_t1_test > burst_threshold).astype(int)
        
        cm_p = confusion_matrix(y_true_labels, y_pred_persistence, labels=[0, 1])
        tn_p, fp_p, fn_p, tp_p = cm_p.ravel()
        acc_p = (tp_p + tn_p) / (tp_p + tn_p + fp_p + fn_p)
        rec_p = tp_p / (tp_p + fn_p) if (tp_p + fn_p) > 0 else 0
        prec_p = tp_p / (tp_p + fp_p) if (tp_p + fp_p) > 0 else 0
        
        # ResNet 變體
        variant_results = []
        
        for variant_name in variant_names:
            variant_info = variants[variant_name]
            model = variant_info['model'].to(device)
            
            checkpoint_path = f'resnet_models/grid{rank}_{variant_name}.pth'
            predictions = load_model_and_predict(model, checkpoint_path, X_test, device)
            
            y_pred = (predictions > burst_threshold).astype(int)
            cm = confusion_matrix(y_true_labels, y_pred, labels=[0, 1])
            tn, fp, fn, tp = cm.ravel()
            
            acc = (tp + tn) / (tp + tn + fp + fn)
            rec = tp / (tp + fn) if (tp + fn) > 0 else 0
            prec = tp / (tp + fp) if (tp + fp) > 0 else 0
            
            variant_results.append({
                'name': variant_info['name'],
                'cm': cm,
                'acc': acc,
                'rec': rec,
                'prec': prec
            })
        
        # 創建混淆矩陣圖
        fig, axes = plt.subplots(2, 3, figsize=(18, 11))
        axes = axes.flatten()
        
        # Persistence
        ax = axes[0]
        cm_percent = cm_p.astype('float') / cm_p.sum() * 100
        annot = np.array([[f'{cm_p[0,0]}\n({cm_percent[0,0]:.1f}%)', 
                          f'{cm_p[0,1]}\n({cm_percent[0,1]:.1f}%)'],
                         [f'{cm_p[1,0]}\n({cm_percent[1,0]:.1f}%)', 
                          f'{cm_p[1,1]}\n({cm_percent[1,1]:.1f}%)']])
        
        sns.heatmap(cm_p, annot=annot, fmt='', cmap='Blues', ax=ax, cbar=True,
                   xticklabels=['預測: 正常', '預測: 爆量'],
                   yticklabels=['真實: 正常', '真實: 爆量'],
                   linewidths=2, linecolor='white', annot_kws={'fontsize': 11, 'weight': 'bold'})
        
        title = f'Persistence (t-1) Baseline\n準確度: {acc_p*100:.1f}% | 召回率: {rec_p*100:.1f}% | 精確度: {prec_p*100:.1f}%'
        ax.set_title(title, fontsize=11, fontweight='bold', pad=12)
        
        # ResNet 變體
        for idx, result in enumerate(variant_results):
            ax = axes[idx + 1]
            cm = result['cm']
            cm_percent = cm.astype('float') / cm.sum() * 100
            
            annot = np.array([[f'{cm[0,0]}\n({cm_percent[0,0]:.1f}%)', 
                              f'{cm[0,1]}\n({cm_percent[0,1]:.1f}%)'],
                             [f'{cm[1,0]}\n({cm_percent[1,0]:.1f}%)', 
                              f'{cm[1,1]}\n({cm_percent[1,1]:.1f}%)']])
            
            sns.heatmap(cm, annot=annot, fmt='', cmap='Greens', ax=ax, cbar=True,
                       xticklabels=['預測: 正常', '預測: 爆量'],
                       yticklabels=['真實: 正常', '真實: 爆量'],
                       linewidths=2, linecolor='white', annot_kws={'fontsize': 11, 'weight': 'bold'})
            
            title = f'{result["name"]}\n準確度: {result["acc"]*100:.1f}% | 召回率: {result["rec"]*100:.1f}% | 精確度: {result["prec"]*100:.1f}%'
            ax.set_title(title, fontsize=11, fontweight='bold', pad=12)
        
        plt.suptitle(f'網格 #{rank}: ({x}, {y}) - {feature} - 爆量預測混淆矩陣 (門檻=1.0σ)', 
                    fontsize=15, fontweight='bold', y=0.995)
        plt.tight_layout()
        
        output_file = f'temp/grid{rank}_confusion_matrices.png'
        fig.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close(fig)
        
        print(f"  ✓ 已儲存混淆矩陣")
    
    print("\n" + "="*80)
    print("✅ 所有圖表生成完成！")
    print("="*80)

if __name__ == '__main__':
    create_all_visualizations()
