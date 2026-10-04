# Change: Add Spatio-Temporal GRU Prediction Pipeline

## Why
We need to build a complete machine learning pipeline to predict crowd flow patterns in spatial grids over time. The current project only has raw data (`data1.csv`) without any prediction capability. This pipeline will enable us to:
- Identify high-traffic grids and predict future crowd density
- Understand which temporal features (近期/週期/周邊) are most important through ablation study
- Focus on predicting "burst events" (爆量時刻) with weighted loss function

## What Changes
- **Grid Selection**: Identify Top 3 grids by total crowd count across 75 days
- **Feature Engineering**: Build comprehensive temporal feature set:
  - Recent features (t-1, t-2, t-3)
  - Periodic features (t-48 for daily, t-336 for weekly)
  - Spatial neighborhood features (3x3 grid mean/max)
  - Time encoding (hour, day of week)
- **Five Model Variants** (Ablation Study):
  1. Benchmark: 2-layer GRU, Hidden=64, full features, Adam optimizer
  2. Fewer layers: 1-layer GRU
  3. No neighborhood: Remove spatial features
  4. No long-term: Remove t-336 weekly feature
  5. Different optimizer: SGD instead of Adam
- **Training Strategy**: 
  - Train on first 60 days, test on last 15 days
  - Weighted MSE loss (5x weight for burst events: n > mean + 1.5*std)
  - 100 epochs with early stopping (patience=10)
- **Visualization**: 6 charts (2 per grid)
  - Time series prediction with burst threshold line
  - Burst event capture capability heatmap/bar chart

## Impact
- **New capabilities**: `data-processing`, `model-training`, `model-evaluation`, `visualization`
- **New files**: 
  - Data scripts: grid selection, feature engineering
  - Model scripts: GRU architecture, 5 training variants
  - Visualization scripts: time series plots, burst analysis
- **Dependencies**: PyTorch, NumPy, Pandas, Matplotlib, scikit-learn (StandardScaler)
