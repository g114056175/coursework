## ADDED Requirements

### Requirement: Model Evaluation Metrics
The system SHALL compute prediction accuracy metrics on test data.

#### Scenario: Overall MAE calculation
- **WHEN** evaluating a trained model on test set
- **THEN** Mean Absolute Error (MAE) is calculated across all test samples
- **AND** MAE is reported for each of the 5 model variants

#### Scenario: Burst-specific MAE
- **WHEN** evaluating burst event predictions
- **THEN** MAE is calculated only for test samples where n > burst_threshold
- **AND** burst MAE is compared across all 5 models

### Requirement: Burst Detection Performance
The system SHALL evaluate binary classification performance for burst events.

#### Scenario: Burst detection accuracy
- **WHEN** a test sample is a true burst event (n > threshold)
- **THEN** system checks if prediction also exceeds threshold
- **AND** accuracy/recall is calculated for burst detection

#### Scenario: Model comparison
- **WHEN** all 5 models are evaluated
- **THEN** burst detection rates are compared across models
- **AND** best-performing model for burst prediction is identified

### Requirement: Per-Grid Evaluation
The system SHALL evaluate models separately for each of the Top 3 grids.

#### Scenario: Independent grid evaluation
- **WHEN** running evaluation pipeline
- **THEN** metrics are computed independently for each grid
- **AND** results show which grid is harder to predict
