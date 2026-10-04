"""
分析 Top 5 網格的時序特徵，推薦最適合建模的 3 個網格

評估指標：
1. 變異係數 (CV) - 穩定性
2. 自相關性 - 時序依賴性
3. 爆量事件頻率 - 預測目標的豐富度
4. 趨勢性 - 是否有明顯模式
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json

plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def analyze_grid_characteristics():
    """分析每個 Top 5 網格的時序特徵"""
    
    # 載入 Top 5 資訊
    with open('results/top5_grids_analysis.json', 'r') as f:
        top5_data = json.load(f)
    
    df_all = pd.read_csv('data1.csv')
    
    results = []
    
    print("="*80)
    print("Top 5 網格時序特徵分析")
    print("="*80)
    
    for grid_info in top5_data['top_grids']:
        x, y = grid_info['x'], grid_info['y']
        rank = grid_info['rank']
        
        # 提取數據
        grid_data = df_all[(df_all['x'] == x) & (df_all['y'] == y)].copy()
        grid_data = grid_data.sort_values(['d', 't'])
        
        n = grid_data['n'].values
        
        # 1. 基本統計
        mean_val = n.mean()
        std_val = n.std()
        max_val = n.max()
        min_val = n.min()
        
        # 2. 變異係數 (CV) - 越小越穩定
        cv = std_val / mean_val if mean_val > 0 else 0
        
        # 3. 自相關性 (lag-1)
        autocorr_1 = np.corrcoef(n[:-1], n[1:])[0, 1] if len(n) > 1 else 0
        
        # 4. 爆量事件頻率 (使用 1.5σ)
        threshold_15 = mean_val + 1.5 * std_val
        burst_count_15 = (n > threshold_15).sum()
        burst_pct_15 = burst_count_15 / len(n) * 100
        
        # 5. 爆量事件頻率 (使用 1.0σ)
        threshold_10 = mean_val + 1.0 * std_val
        burst_count_10 = (n > threshold_10).sum()
        burst_pct_10 = burst_count_10 / len(n) * 100
        
        # 6. 零值比例
        zero_pct = (n == 0).sum() / len(n) * 100
        
        # 7. 日週期性（比較相鄰日同時段的相關性）
        daily_autocorr = np.corrcoef(n[:-48], n[48:])[0, 1] if len(n) > 48 else 0
        
        results.append({
            'rank': rank,
            'x': x,
            'y': y,
            'mean': mean_val,
            'std': std_val,
            'cv': cv,
            'autocorr_1': autocorr_1,
            'daily_autocorr': daily_autocorr,
            'burst_15_pct': burst_pct_15,
            'burst_10_pct': burst_pct_10,
            'zero_pct': zero_pct,
            'max': max_val,
            'total_flow': grid_info['total_flow']
        })
        
        print(f"\n網格 #{rank} ({x}, {y})")
        print("-"*80)
        print(f"  總人流: {grid_info['total_flow']:,}")
        print(f"  平均值: {mean_val:.2f}, 標準差: {std_val:.2f}, 最大值: {max_val:.0f}")
        print(f"  變異係數 (CV): {cv:.3f} {'(穩定)' if cv < 0.7 else '(波動大)'}")
        print(f"  Lag-1 自相關: {autocorr_1:.3f} {'(強依賴)' if autocorr_1 > 0.8 else '(中等)'}")
        print(f"  日週期相關: {daily_autocorr:.3f} {'(明顯)' if daily_autocorr > 0.5 else '(弱)'}")
        print(f"  爆量比例 (1.5σ): {burst_pct_15:.2f}%")
        print(f"  爆量比例 (1.0σ): {burst_pct_10:.2f}%")
        print(f"  零值比例: {zero_pct:.2f}%")
    
    return pd.DataFrame(results)

def recommend_grids(df):
    """推薦最適合建模的 3 個網格"""
    
    print(f"\n{'='*80}")
    print("📊 建模適合度評分")
    print(f"{'='*80}\n")
    
    # 評分標準（總分 100）
    scores = []
    
    for _, row in df.iterrows():
        score_breakdown = {}
        total_score = 0
        
        # 1. 總人流量 (20分) - 越多越好
        flow_score = min(20, (row['total_flow'] / df['total_flow'].max()) * 20)
        score_breakdown['人流量'] = flow_score
        total_score += flow_score
        
        # 2. 數據穩定性 (15分) - CV 適中最好 (0.6-0.9)
        cv = row['cv']
        if 0.6 <= cv <= 0.9:
            cv_score = 15
        elif 0.5 <= cv < 0.6 or 0.9 < cv <= 1.0:
            cv_score = 10
        else:
            cv_score = 5
        score_breakdown['穩定性'] = cv_score
        total_score += cv_score
        
        # 3. Lag-1 自相關 (20分) - 越高越好（更易預測）
        autocorr_score = row['autocorr_1'] * 20
        score_breakdown['時序依賴'] = autocorr_score
        total_score += autocorr_score
        
        # 4. 日週期性 (15分) - 越強越好
        daily_score = row['daily_autocorr'] * 15 if row['daily_autocorr'] > 0 else 0
        score_breakdown['週期性'] = daily_score
        total_score += daily_score
        
        # 5. 爆量豐富度 (20分) - 1.0σ 下 10-20% 最佳
        burst_pct = row['burst_10_pct']
        if 10 <= burst_pct <= 20:
            burst_score = 20
        elif 5 <= burst_pct < 10 or 20 < burst_pct <= 25:
            burst_score = 15
        else:
            burst_score = 10
        score_breakdown['爆量豐富度'] = burst_score
        total_score += burst_score
        
        # 6. 數據完整性 (10分) - 零值越少越好
        completeness_score = max(0, 10 - row['zero_pct'])
        score_breakdown['完整性'] = completeness_score
        total_score += completeness_score
        
        scores.append({
            'rank': row['rank'],
            'x': row['x'],
            'y': row['y'],
            'total_score': total_score,
            **score_breakdown
        })
    
    scores_df = pd.DataFrame(scores).sort_values('total_score', ascending=False)
    
    print(f"{'網格':<15} {'總分':<8} {'人流量':<10} {'穩定性':<10} {'時序':<10} {'週期':<10} {'爆量':<10} {'完整':<8}")
    print("-"*80)
    
    for _, row in scores_df.iterrows():
        print(f"({row['x']:.0f}, {row['y']:.0f}) #{row['rank']:<3} "
              f"{row['total_score']:<8.1f} "
              f"{row['人流量']:<10.1f} "
              f"{row['穩定性']:<10.1f} "
              f"{row['時序依賴']:<10.1f} "
              f"{row['週期性']:<10.1f} "
              f"{row['爆量豐富度']:<10.1f} "
              f"{row['完整性']:<8.1f}")
    
    # 選出 Top 3
    top3 = scores_df.head(3)
    
    print(f"\n{'='*80}")
    print("🎯 推薦建模網格 (Top 3)")
    print(f"{'='*80}\n")
    
    for idx, row in top3.iterrows():
        print(f"✅ 推薦 #{top3.index.get_loc(idx) + 1}: 網格 ({row['x']:.0f}, {row['y']:.0f}) - 原排名 #{row['rank']}")
        print(f"   總分: {row['total_score']:.1f}/100")
        print()
    
    return top3, scores_df

def visualize_comparison(df, scores_df):
    """視覺化比較"""
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # 合併數據
    comparison = df.merge(scores_df[['rank', 'total_score']], on='rank')
    comparison = comparison.sort_values('total_score', ascending=False)
    
    # 1. 總分比較
    ax = axes[0]
    colors = ['gold', 'silver', '#CD7F32', 'lightblue', 'lightgray']
    bars = ax.bar(range(len(comparison)), comparison['total_score'], color=colors)
    ax.set_xticks(range(len(comparison)))
    ax.set_xticklabels([f"({r['x']:.0f},{r['y']:.0f})" for _, r in comparison.iterrows()], 
                       rotation=45, ha='right')
    ax.set_ylabel('總分', fontsize=12)
    ax.set_title('建模適合度總分', fontsize=14, fontweight='bold')
    ax.set_ylim([0, 100])
    ax.grid(True, alpha=0.3, axis='y')
    
    # 標註分數
    for i, (_, row) in enumerate(comparison.iterrows()):
        ax.text(i, row['total_score'] + 2, f"{row['total_score']:.1f}", 
               ha='center', fontsize=10, fontweight='bold')
    
    # 2. 關鍵指標雷達圖（Top 3）
    ax = axes[1]
    top3_data = comparison.head(3)
    
    categories = ['CV\n(穩定)', 'Lag-1\n自相關', '日週期\n相關', '爆量\n(1.0σ)', '完整性']
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]
    
    ax = plt.subplot(132, projection='polar')
    
    for idx, row_data in top3_data.iterrows():
        # 正規化到 0-1
        values = [
            1 - min(1, row_data['cv']),  # CV 越小越好，反轉
            row_data['autocorr_1'],
            row_data['daily_autocorr'],
            row_data['burst_10_pct'] / 20,  # 正規化到 0-1
            1 - row_data['zero_pct'] / 100
        ]
        values += values[:1]
        
        label = f"({row_data['x']:.0f},{row_data['y']:.0f})"
        ax.plot(angles, values, 'o-', linewidth=2, label=label)
        ax.fill(angles, values, alpha=0.15)
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=9)
    ax.set_ylim(0, 1)
    ax.set_title('Top 3 關鍵指標比較', fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=9)
    ax.grid(True)
    
    # 3. 變異係數 vs 自相關
    ax = axes[2]
    
    colors_scatter = ['gold' if i < 3 else 'lightgray' for i in range(len(comparison))]
    sizes = [300 if i < 3 else 150 for i in range(len(comparison))]
    
    for idx, (i, row) in enumerate(comparison.iterrows()):
        ax.scatter(row['cv'], row['autocorr_1'], 
                  s=sizes[idx], c=colors_scatter[idx], 
                  edgecolors='black', linewidths=2, alpha=0.7, zorder=10-idx)
        ax.annotate(f"({row['x']:.0f},{row['y']:.0f})", 
                   xy=(row['cv'], row['autocorr_1']), 
                   xytext=(5, 5), textcoords='offset points',
                   fontsize=9, fontweight='bold' if idx < 3 else 'normal')
    
    ax.set_xlabel('變異係數 (CV)', fontsize=12)
    ax.set_ylabel('Lag-1 自相關', fontsize=12)
    ax.set_title('穩定性 vs 可預測性', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0.8, color='red', linestyle='--', alpha=0.5, label='強相關門檻')
    ax.axvline(x=0.7, color='orange', linestyle='--', alpha=0.5, label='穩定性門檻')
    ax.legend(fontsize=9)
    
    plt.tight_layout()
    return fig

def main():
    # 分析
    df = analyze_grid_characteristics()
    
    # 推薦
    top3, scores_df = recommend_grids(df)
    
    # 視覺化
    fig = visualize_comparison(df, scores_df)
    fig.savefig('results/grid_selection_analysis.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    
    print("\n✓ 分析圖表已儲存: results/grid_selection_analysis.png")
    
    # 儲存推薦結果
    selected = top3[['rank', 'x', 'y', 'total_score']].to_dict('records')
    
    output = {
        'selected_grids': [
            {
                'selection_rank': i+1,
                'original_rank': int(r['rank']),
                'x': int(r['x']),
                'y': int(r['y']),
                'score': float(r['total_score'])
            }
            for i, r in enumerate(selected)
        ]
    }
    
    with open('results/recommended_grids.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print("✓ 推薦結果已儲存: results/recommended_grids.json")

if __name__ == '__main__':
    main()
