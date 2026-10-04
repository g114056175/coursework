## Context
Building a complete spatio-temporal crowd flow prediction system requires careful consideration of feature engineering, model architecture, and evaluation strategies. This design document outlines key technical decisions.

## Goals / Non-Goals
**Goals**:
- Create reproducible pipeline for Top 3 grids independently
- Conduct ablation study to understand feature importance
- Focus on burst event (爆量) prediction accuracy
- Generate interpretable visualizations

**Non-Goals**:
- Training a single model for all grids (we train per-grid models)
- Real-time prediction API (offline batch prediction only)
- Multi-step ahead forecasting (only single time-step t+1)
- Advanced architectures like Transformers or ST-ResNet (keeping it simple with GRU)

## Decisions

### Decision 1: Residual vs Direct Prediction
**Choice**: Predict residual $Y_t - Y_{t-48}$ and restore

**Alternatives**:
- Direct prediction of $Y_t$: Simpler but harder to learn daily patterns
- Both approaches: More complex, harder to compare

**Rationale**: Residual learning has shown better performance in time-series prediction by capturing deviations from daily patterns rather than absolute values. The t-48 lag provides a strong baseline.

### Decision 2: Per-Grid Training
**Choice**: Train separate models for each of Top 3 grids

**Alternatives**:
- Single global model with grid embeddings
- Multi-task learning across grids

**Rationale**: Each grid may have unique crowd patterns (business district vs residential). Separate models allow specialization and easier debugging. With only 3 grids, training cost is manageable.

### Decision 3: GRU vs LSTM vs Transformer
**Choice**: GRU (Gated Recurrent Units)

**Alternatives**:
- LSTM: More parameters, similar performance
- Transformer: Overkill for this problem size, harder to interpret

**Rationale**: GRU provides good balance between expressiveness and training speed. Fewer parameters than LSTM reduce overfitting risk with limited data.

### Decision 4: Weighted Loss for Burst Events
**Choice**: 5x weight for samples where $n > \mu + 1.5\sigma$

**Alternatives**:
- Focal loss: More complex, harder to tune
- Separate burst detection classifier: Two-stage approach, more complex

**Rationale**: Simple weighted MSE directly optimizes what we care about (burst prediction) while still learning from normal samples. The 5x multiplier can be tuned if needed.

### Decision 5: Spatial Feature Encoding
**Choice**: 3x3 neighborhood mean and max at t-1

**Alternatives**:
- Graph neural network: Too complex for sparse grid data
- Convolutional layers: Requires dense grid representation
- Distance-weighted features: Complex computation

**Rationale**: Mean captures average neighborhood activity, max captures peak activity in surrounding area. Simple aggregation handles sparse data naturally (missing grids = 0).

## Architecture Diagram

```
Input Features (per sample):
├─ Recent: [n_{t-1}, n_{t-2}, n_{t-3}]
├─ Periodic: [n_{t-48}, n_{t-336}]
├─ Spatial: [mean_neighbor_{t-1}, max_neighbor_{t-1}]
└─ Temporal: [hour, day_of_week]
       ↓
  StandardScaler (fit on train only)
       ↓
  GRU Layers (1 or 2 layers, hidden=64)
       ↓
  MLP Head (Linear → ReLU → Linear)
       ↓
  Output: Residual prediction (Ŷ_t - Y_{t-48})
       ↓
  Restore: Ŷ_t = prediction + Y_{t-48}
```

## Data Split Strategy
- **Train**: Days 0-59 (first 60 days)
- **Test**: Days 60-74 (last 15 days)
- **Rationale**: 80/20 split, chronological to respect temporal order

## Burst Threshold Calculation
```python
train_mean = train_data['n'].mean()
train_std = train_data['n'].std()
burst_threshold = train_mean + 1.5 * train_std
```
All samples with `n > burst_threshold` get 5x loss weight.

## Feature Handling for Early Days
- **t-48**: Available from day 1 onward (use 0 for day 0)
- **t-336**: Available from day 7 onward (use 0 for days 0-6)
This zero-padding is acceptable as these early samples are in the training set.

## Model Configurations

| Model | Layers | Hidden | Features | Optimizer | Learning Rate |
|-------|--------|--------|----------|-----------|---------------|
| 1 (Benchmark) | 2 | 64 | All | Adam | 0.001 |
| 2 (Fewer layers) | 1 | 64 | All | Adam | 0.001 |
| 3 (No spatial) | 2 | 64 | No neighborhood | Adam | 0.001 |
| 4 (No weekly) | 2 | 64 | No t-336 | Adam | 0.001 |
| 5 (SGD) | 2 | 64 | All | SGD | 0.01 |

## Risks / Trade-offs

**Risk 1: Data Sparsity**
- Many grids may have zero counts in many time slots
- **Mitigation**: Focus on Top 3 grids ensures sufficient data density

**Risk 2: Cold Start (t-336 unavailable early)**
- First 7 days don't have weekly lag feature
- **Mitigation**: Zero-padding for missing lags; all test data has full features

**Risk 3: Overfitting with 5 Models**
- Training 5 models per grid (15 total) increases risk
- **Mitigation**: Early stopping with validation split; simple architecture (only 2 layers max)

**Risk 4: Class Imbalance (Burst vs Normal)**
- Burst events may be rare
- **Mitigation**: Weighted loss function addresses this directly

## Verification Plan
1. **Data integrity checks**: Verify Top 3 grids have sufficient samples
2. **Feature shape validation**: Ensure all feature matrices have correct dimensions
3. **Training convergence**: Monitor loss curves for all 5 models
4. **Ablation effectiveness**: Models 3 and 4 should show performance drop if features are important
5. **Visualization quality**: All 6 charts should be generated and interpretable

## Open Questions
- **Q1**: Should we use dropout for regularization?
  - **Answer**: Start without dropout; add if overfitting observed
- **Q2**: Should we tune the 5x burst weight?
  - **Answer**: Start with 5x; can experiment with [3x, 5x, 10x] if needed
- **Q3**: Should we add validation set for early stopping?
  - **Answer**: Use 10% of training data (days 0-53 train, days 54-59 val)
