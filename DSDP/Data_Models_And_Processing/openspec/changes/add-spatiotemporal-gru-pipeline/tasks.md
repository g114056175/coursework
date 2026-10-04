## 1. Data Preparation
- [ ] 1.1 Create `01_grid_selection.py`: Load data1.csv and identify Top 3 grids by total count
- [ ] 1.2 Save Top 3 grid coordinates to config file for reuse
- [ ] 1.3 Validate data quality (check for missing time periods, outliers)

## 2. Feature Engineering
- [ ] 2.1 Create `02_feature_engineering.py`: Build temporal feature matrix
- [ ] 2.2 Implement lag features: t-1, t-2, t-3
- [ ] 2.3 Implement periodic features: t-48 (daily), t-336 (weekly) with zero-padding for early days
- [ ] 2.4 Implement spatial neighborhood features: 3x3 grid mean and max at t-1
- [ ] 2.5 Add time encoding: hour (0-47), day of week (0-6)
- [ ] 2.6 Apply StandardScaler normalization to all features
- [ ] 2.7 Define burst threshold: mean + 1.5*std from training data
- [ ] 2.8 Split data: first 60 days train, last 15 days test

## 3. Model Architecture
- [ ] 3.1 Create `03_model_architecture.py`: Define GRU+MLP PyTorch module
- [ ] 3.2 Implement configurable GRU layers (1 or 2 layers)
- [ ] 3.3 Implement MLP head for final prediction
- [ ] 3.4 Create feature selection mechanism for ablation variants

## 4. Training Pipeline (5 Variants)
- [ ] 4.1 Create `04_train_models.py`: Training script for all 5 model variants
- [ ] 4.2 Implement Model 1 (Benchmark): 2-layer GRU, hidden=64, Adam lr=0.001
- [ ] 4.3 Implement Model 2 (1-layer): 1-layer GRU variant
- [ ] 4.4 Implement Model 3 (no spatial): Remove neighborhood features
- [ ] 4.5 Implement Model 4 (no weekly): Remove t-336 feature
- [ ] 4.6 Implement Model 5 (SGD): Use SGD optimizer lr=0.01
- [ ] 4.7 Implement weighted MSE loss (5x for burst events, 1x for normal)
- [ ] 4.8 Add early stopping with patience=10
- [ ] 4.9 Save best model checkpoints for each variant

## 5. Evaluation
- [ ] 5.1 Create `05_evaluate_models.py`: Test all 5 models on test set
- [ ] 5.2 Generate predictions for all test samples
- [ ] 5.3 Calculate overall MAE for each model
- [ ] 5.4 Calculate MAE specifically for burst events
- [ ] 5.5 Calculate burst detection accuracy (binary: predicted > threshold)

## 6. Visualization
- [ ] 6.1 Create `06_visualize_results.py`: Generate 6 charts
- [ ] 6.2 For each Top 3 grid:
  - [ ] 6.2.1 Time series plot: ground truth + 5 model predictions + burst threshold line
  - [ ] 6.2.2 Burst analysis chart: MAE and detection rate for each model on burst events
- [ ] 6.3 Save all visualizations to `results/` directory

## 7. Documentation
- [ ] 7.1 Create README.md with execution instructions
- [ ] 7.2 Document feature descriptions and model configurations
- [ ] 7.3 Add interpretation guide for visualizations
