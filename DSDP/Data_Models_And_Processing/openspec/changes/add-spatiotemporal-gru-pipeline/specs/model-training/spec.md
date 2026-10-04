## ADDED Requirements

### Requirement: GRU Architecture
The system SHALL implement a GRU-based neural network for time-series prediction.

#### Scenario: Configurable GRU layers
- **WHEN** model is initialized
- **THEN** number of GRU layers (1 or 2) is configurable
- **AND** hidden size is configurable (default: 64)

#### Scenario: MLP prediction head
- **WHEN** GRU output is produced
- **THEN** MLP head (Linear → ReLU → Linear) maps to final prediction
- **AND** output is a single scalar (residual prediction)

#### Scenario: Residual learning
- **WHEN** making a prediction for time t
- **THEN** model predicts residual: Ŷ_t - Y_{t-48}
- **AND** final prediction is restored: Ŷ_t = residual + Y_{t-48}

### Requirement: Five Model Variants
The system SHALL support five distinct model configurations for ablation study.

#### Scenario: Model 1 - Benchmark
- **WHEN** training baseline model
- **THEN** 2 GRU layers with hidden size 64 are used
- **AND** all features are included
- **AND** Adam optimizer with lr=0.001 is used

#### Scenario: Model 2 - Fewer Layers
- **WHEN** training single-layer variant
- **THEN** 1 GRU layer with hidden size 64 is used
- **AND** all other settings match Model 1

#### Scenario: Model 3 - No Spatial Features
- **WHEN** training without neighborhood features
- **THEN** spatial mean and max features are excluded
- **AND** all other settings match Model 1

#### Scenario: Model 4 - No Weekly Periodicity
- **WHEN** training without long-term lag
- **THEN** t-336 weekly feature is excluded
- **AND** all other settings match Model 1

#### Scenario: Model 5 - SGD Optimizer
- **WHEN** training with different optimizer
- **THEN** SGD optimizer with lr=0.01 is used instead of Adam
- **AND** all other settings match Model 1

### Requirement: Weighted Loss Function
The system SHALL use weighted MSE loss to prioritize burst event prediction.

#### Scenario: Loss weighting
- **WHEN** computing loss for a training sample
- **THEN** burst event samples (n > threshold) receive 5.0x weight
- **AND** normal samples receive 1.0x weight

### Requirement: Early Stopping
The system SHALL implement early stopping to prevent overfitting.

#### Scenario: Validation monitoring
- **WHEN** training for up to 100 epochs
- **THEN** validation loss is monitored every epoch
- **AND** training stops if validation loss doesn't improve for 10 consecutive epochs

#### Scenario: Best model checkpoint
- **WHEN** training completes or early stops
- **THEN** model weights with lowest validation loss are saved
- **AND** checkpoint includes model configuration metadata
