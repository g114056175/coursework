## ADDED Requirements

### Requirement: Grid Selection
The system SHALL identify the Top 3 grids by total crowd count across all time periods.

#### Scenario: Load and aggregate data
- **WHEN** data1.csv is loaded
- **THEN** system computes total crowd count for each unique (x,y) grid
- **AND** system selects the 3 grids with highest total count

#### Scenario: Save grid configuration
- **WHEN** Top 3 grids are identified
- **THEN** grid coordinates are saved to a configuration file
- **AND** configuration file includes grid rank and total count

### Requirement: Feature Engineering
The system SHALL construct temporal and spatial features for each grid time-series.

#### Scenario: Lag features
- **WHEN** building features for time t
- **THEN** recent lag features (t-1, t-2, t-3) are included
- **AND** periodic lag features (t-48, t-336) are included with zero-padding for unavailable periods

#### Scenario: Spatial neighborhood features
- **WHEN** computing spatial features for grid (x,y) at time t-1
- **THEN** system computes mean crowd count of 3x3 neighborhood grids
- **AND** system computes max crowd count of 3x3 neighborhood grids
- **AND** missing neighbor grids are treated as zero count

#### Scenario: Time encoding
- **WHEN** creating time features
- **THEN** hour of day (0-47) is included as a feature
- **AND** day of week (0-6) is included as a feature

#### Scenario: Feature normalization
- **WHEN** features are constructed
- **THEN** StandardScaler is fit on training data only
- **AND** same scaler transforms both training and test features

### Requirement: Data Splitting
The system SHALL split data chronologically into train and test sets.

#### Scenario: Chronological split
- **WHEN** splitting data for a grid
- **THEN** first 60 days (d=0 to d=59) are used for training
- **AND** last 15 days (d=60 to d=74) are used for testing

### Requirement: Burst Threshold Definition
The system SHALL define burst events based on training data statistics.

#### Scenario: Calculate threshold
- **WHEN** training data is available
- **THEN** burst threshold is mean + 1.5 * standard deviation
- **AND** threshold is computed separately for each grid

#### Scenario: Label burst events
- **WHEN** a sample has crowd count n > burst_threshold
- **THEN** sample is labeled as a burst event
- **AND** burst label is used for weighted loss calculation
