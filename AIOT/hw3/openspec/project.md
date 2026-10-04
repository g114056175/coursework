# Project Context

## Purpose
AIOT 課程第三次作業：使用 OpenSpec 和 AI Coding CLI 實作 Spam Email 分類系統。
主要目標：
- 實作垃圾郵件分類模型
- 建立 Streamlit 展示介面
- 使用 OpenSpec 管理開發流程
- 整合 AI 輔助開發工具提升效率

## Tech Stack
- 核心框架：Python, Streamlit
- AI/ML：scikit-learn, NLTK/SpaCy
- 資料處理：pandas, numpy
- 視覺化：matplotlib, seaborn
- 開發工具：
  - GitHub Copilot（AI 輔助）
  - VS Code（IDE）
  - OpenSpec（規格管理）
  - Git（版本控制）
- 部署：Streamlit Cloud

## Project Conventions

### Code Style
- Python 代碼遵循 PEP 8 規範
- 使用清晰的命名約定：
  - 模型相關：XxxModel, XxxClassifier
  - 數據處理：XxxProcessor, XxxTransformer
  - 工具函數：xxx_util, process_xxx
- 必要的文檔字符串（docstring）
- 適當的代碼註釋
- 遵循 Streamlit 最佳實踐

### Architecture Patterns
- 模組化設計：
  - data_processing/：數據預處理
  - models/：ML 模型實現
  - visualization/：結果視覺化
  - streamlit_app.py：Web 界面
- 清晰的職責分離
- 使用 OpenSpec 管理需求與變更
- 重視代碼可維護性與可重用性

### Testing Strategy
- 模型評估指標：
  - 準確率（Accuracy）
  - 精確率（Precision）
  - 召回率（Recall）
  - F1 分數
- 數據驗證：
  - 預處理後的數據質量
  - 訓練/測試集分布
- 使用 OpenSpec 的 Scenarios 作為測試案例

### Git Workflow
- 主分支：main
- 功能分支命名：
  - feature/data-preprocessing
  - feature/model-implementation
  - feature/streamlit-ui
- 每個重要功能使用 Pull Request
- 遵循 OpenSpec 變更流程

## Domain Context
- 垃圾郵件分類問題特性
- NLP 處理技術
- 機器學習模型選擇
- 特徵工程最佳實踐
- Streamlit 應用開發
- AI 輔助開發工具使用

## Important Constraints
- 參考項目要求：
  - 需實現完整的分類功能
  - 必須有 Streamlit 展示介面
  - 代碼需開源於 GitHub
- 性能要求：
  - 模型準確率達到基準水平
  - Streamlit 應用響應及時
- 時間限制：課程進度
- OpenSpec 與 AI 工具使用規範

## External Dependencies
- 參考資源：
  - Packt AI for Cybersecurity 倉庫
  - Streamlit 官方文檔
- 主要依賴：
  - scikit-learn
  - NLTK/SpaCy
  - pandas, numpy
  - streamlit
- 開發工具：
  - GitHub Copilot
  - OpenSpec CLI
- 部署平台：
  - GitHub
  - Streamlit Cloud
