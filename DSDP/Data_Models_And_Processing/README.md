# 時空人流預測 - ResNet深度學習模型

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-complete-success.svg)

基於ResNet架構的時空人流預測系統，使用台北市75天（3,600時段）的網格人流數據。

## 🎯 專案目標

預測指定網格的未來人流量，並提供人流爆量預警，輔助交通管控和人流疏散決策。

## 📊 數據概覽

- **時間範圍**: 75天（3,600個時段，每時段30分鐘）
- **空間範圍**: 200×200網格（40,000個網格）
- **記錄總數**: 9,614,255筆
- **選定網格**: 3個（最高人流、第二高人流、最大瞬間湧入）

## 📥 數據下載

由於原始數據文件 `data1.csv` (142.5MB) 超過GitHub檔案大小限制，請從以下連結下載：

**🔗 [下載 data1.csv from Google Drive](https://drive.google.com/file/d/1vRWOoXnDL0aL0I9UQzt0XVc78vWOiySe/view?usp=drive_link)**

下載後請將文件放置於專案根目錄。

## 🚀 快速開始

### 環境設置

```bash
# 克隆專案
git clone https://github.com/g114056175/coursework.git
cd coursework/DSDP/Data_Models_And_Processing

# 安裝依賴
pip install -r requirements.txt

# 下載數據文件（見上方連結）
# 將 data1.csv 放置於根目錄
```

### 完整執行流程

```bash
# 1. 空間分析（識別高人流網格）
python 22_spatial_analysis.py

# 2. Baseline評估
python 27_persistence_baseline_analysis.py

# 3. 特徵工程（提取69維特徵）
python 28_resnet_feature_engineering.py

# 4. 訓練ResNet模型（約10-15分鐘）
python 30_train_resnet.py

# 5. 評估與視覺化
python 34_regenerate_all_with_1sigma.py
```

## 📁 重要資料夾

| 資料夾 | 說明 |
|--------|------|
| `grid_selection/` | 網格選擇相關圖表（11張） |
| `temp/` | 模型評估結果（18張圖表） |
| `resnet_models/` | 訓練好的模型（15個.pth檔） |
| `resnet_features/` | 特徵數據（3個網格） |
| `archived_scripts/` | 歸檔的測試腳本 |

## 🎯 選定網格

| # | 座標 | 特徵 | 累積人流 | MAE (最佳) |
|---|------|------|----------|-----------|
| 1 | (80, 95) | 最高人流 | 122,068 | 3.84 (Deep) |
| 2 | (80, 93) | 第二高人流 | 113,517 | 3.25 (Wide) |
| 3 | (79, 97) | 最大瞬間湧入 | 24,308 | 1.75 (GELU) |

## 🤖 模型變體

訓練了5個ResNet變體：

1. **Baseline ResNet**: 3層, 128隱藏單元, ReLU
2. **Deep ResNet**: 6層, 128隱藏單元, ReLU（更深）
3. **Wide ResNet**: 3層, 256隱藏單元, ReLU（更寬）
4. **LeakyReLU ResNet**: 3層, 128隱藏單元, LeakyReLU
5. **GELU ResNet**: 3層, 128隱藏單元, GELU（現代激活）

## 📈 核心成果

### vs Persistence Baseline

- **MAE 降低**: 40-48%
- **爆量召回率提升**: 從66%到84-88%
- **訓練速度**: 比LSTM快3-5倍

### 最佳模型

- **網格1**: Deep ResNet (MAE=3.84)
- **網格2**: Wide ResNet (MAE=3.25)
- **網格3**: GELU ResNet (MAE=1.75)

## 🔬 技術特點

### 特徵工程（69維）

- **Lag特徵**: t-1, t-2, ..., t-6, t-48, t-96, t-336
- **統計特徵**: Rolling mean/std/min/max (12時段窗口)
- **時間編碼**: 48小時 + 7天 + 週末標記

### 訓練策略

- **損失函數**: Weighted MSE（爆量事件5x權重）
- **優化器**: Adam (lr=1e-3)
- **正則化**: Dropout(0.2) + Weight Decay(1e-5)
- **早停**: Patience=25 epochs
- **數據分割**: 60天訓練 / 15天測試

## 📚 文檔

- **PROJECT_STRUCTURE.md** - 完整專案結構說明
- **grid_selection/README.md** - 網格選擇詳細分析
- **Brain artifacts** - 技術設計文檔
  - `resnet_model_design.md`
  - `model_comparison_resnet_vs_rnn.md`
  - `report_writing_guide.md`

## 🛠️ 核心腳本說明

| 腳本 | 功能 |
|------|------|
| `22_spatial_analysis.py` | 空間分析與Top5識別 |
| `27_persistence_baseline_analysis.py` | Persistence baseline評估 |
| `28_resnet_feature_engineering.py` | ResNet特徵工程 |
| `29_resnet_models.py` | ResNet模型定義 |
| `30_train_resnet.py` | 模型訓練 |
| `34_regenerate_all_with_1sigma.py` | 完整評估與視覺化 |

## 📊 輸出圖表

### grid_selection/ (11張)
- 3張時序圖
- 3張選擇理由熱圖
- 1張空間熱圖
- 2張baseline分析圖
- 1張對比圖

### temp/ (18張)
- 15張預測對比圖（3網格 × 5模型）
- 3張混淆矩陣

## 🎓 為什麼選擇ResNet？

1. **訓練速度快**: 比LSTM快3-5倍（並行處理）
2. **梯度穩定**: 殘差連接完全解決梯度消失
3. **多維特徵**: 擅長處理69維特徵組合
4. **可解釋性**: 明確的特徵工程，非黑盒模型
5. **實驗效率**: 快速迭代，易於調參

詳見: `model_comparison_resnet_vs_rnn.md`

## 📝 報告撰寫

參考 `report_writing_guide.md`，包含：
- 兩階段完整流程
- 所需圖表清單
- 文字說明範本
- 核心發現總結

## 🔧 故障排除

### 記憶體不足
```bash
# 減少批次大小（在 30_train_resnet.py 中）
batch_size = 32  # 改為32或16
```

### 訓練太慢
```bash
# 使用GPU（如果有）
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
```

## 授權

本專案採用 MIT License - 詳見 [LICENSE](LICENSE) 文件

本專案供學術研究使用，如使用請引用本專案。

---

**最後更新**: 2025-12-26  
**版本**: 2.0  
**狀態**: ✅ 已清理並準備推送GitHub

