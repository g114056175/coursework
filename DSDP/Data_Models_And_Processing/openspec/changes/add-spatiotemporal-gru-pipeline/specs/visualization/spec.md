## ADDED Requirements

### Requirement: Time Series Prediction Plots
The system SHALL generate time-series visualization comparing predictions to ground truth.

#### Scenario: Multi-model comparison plot
- **WHEN** creating time-series plot for a grid
- **THEN** X-axis shows test time points (days 60-74, times 0-47)
- **AND** Y-axis shows crowd count (n)
- **AND** ground truth is plotted as black line
- **AND** all 5 model predictions are plotted in different colors

#### Scenario: Burst threshold visualization
- **WHEN** time-series plot is generated
- **THEN** burst threshold (mean + 1.5*std) is shown as red dashed horizontal line
- **AND** actual burst events are visually distinguishable

#### Scenario: Plot metadata
- **WHEN** saving time-series plot
- **THEN** plot title includes grid coordinates (x, y)
- **AND** legend clearly identifies each model variant
- **AND** axes are labeled with units

### Requirement: Burst Capture Analysis Charts
The system SHALL generate visualizations showing model performance on burst events.

#### Scenario: Burst MAE comparison
- **WHEN** creating burst analysis chart
- **THEN** chart displays MAE for each of 5 models on burst events only
- **AND** chart type is bar chart or heatmap

#### Scenario: Burst detection rate
- **WHEN** analyzing burst prediction capability
- **THEN** chart shows percentage of burst events correctly predicted above threshold
- **AND** best and worst models are visually distinguishable

### Requirement: Output Organization
The system SHALL save all visualizations to organized directory structure.

#### Scenario: File naming convention
- **WHEN** saving visualization files
- **THEN** filenames include grid identifier and plot type
- **AND** format is PNG or PDF with high resolution (300 DPI minimum)

#### Scenario: Results directory
- **WHEN** generating all 6 charts (2 per grid × 3 grids)
- **THEN** charts are saved to `results/` directory
- **AND** directory structure allows easy identification of which grid each chart represents
