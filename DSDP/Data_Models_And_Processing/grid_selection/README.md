# Grid Selection for Spatio-Temporal Crowd Flow Prediction

## Selected Grids Overview

This folder contains time-series visualizations for the **3 selected grids** used in the spatio-temporal crowd flow prediction analysis.

---

## Selection Criteria

The grids were selected based on:
1. **Clear Feature Characteristics** - Each grid has a distinct, measurable property
2. **Geographic Diversity** - Grids are spatially distant (>50 units apart)
3. **Pattern Variety** - Different crowd flow behaviors for robust model training

---

## Selected Grids

### Grid #1: (80, 95) - Highest Traffic Hub 🏆
- **Feature**: Highest cumulative crowd flow
- **Total Flow**: 122,068 people (75 days)
- **Characteristics**:
  - Average: 34.0 people/period
  - Peak: 126 people
  - Coefficient of Variation (CV): 0.70
- **Why Selected**: 
  - Represents the **busiest commercial/transit center**
  - Stable and predictable patterns
  - Rich data for model training
- **Use Case**: Baseline for high-traffic prediction

---

### Grid #2: (34, 44) - Maximum Surge Location 📈
- **Feature**: Largest single-period crowd increase
- **Total Flow**: 24,841 people (75 days)
- **Characteristics**:
  - Average: 7.2 people/period
  - Peak: 33 people
  - Max increase: +25 people in one period
- **Why Selected**: 
  - Sudden **burst events** and rapid changes
  - Low baseline with sharp spikes
  - Tests model's ability to predict **event-driven surges**
- **Use Case**: Event detection and anomaly prediction

---

### Grid #3: (86, 149) - Highest Volatility Zone 📊
- **Feature**: Highest coefficient of variation (CV)
- **Total Flow**: 42,412 people (75 days)
- **Characteristics**:
  - Average: 12.0 people/period
  - Peak: 141 people (extreme outlier)
  - CV: 0.89 (highly unstable)
- **Why Selected**: 
  - **Extremely unpredictable** patterns
  - Large gap between average and peak
  - Tests model's robustness to high volatility
- **Use Case**: Challenging prediction scenario

---

## Spatial Distribution

| Grid Pair | Distance (units) | Status |
|-----------|------------------|--------|
| #1 ↔ #2 | 68.7 | ✅ Well separated |
| #1 ↔ #3 | 54.3 | ✅ Well separated |
| #2 ↔ #3 | 117.2 | ✅ Very distant |

The three grids form a **triangular spatial distribution**, ensuring geographic diversity and minimizing spatial correlation.

---

## Files in This Folder

1. **grid_1_80_95_最高人流.png** - Time series for Grid #1 (Highest Traffic)
2. **grid_2_34_44_最大瞬間湧入.png** - Time series for Grid #2 (Max Surge)
3. **grid_3_86_149_最高波動性.png** - Time series for Grid #3 (Highest Volatility)
4. **comparison_all_grids.png** - Side-by-side comparison of all three grids
5. **README.md** - This file

---

## Key Takeaways

**Why These 3 Grids?**
- ✅ **Diversity**: High vs. Medium vs. Low traffic
- ✅ **Distinct Patterns**: Stable vs. Surge-driven vs. Volatile
- ✅ **Geographic Spread**: No clustering, independent locations
- ✅ **Clear Features**: Each has a measurable, unique characteristic

**Model Training Value**:
- Grid #1: Learn stable high-traffic patterns
- Grid #2: Detect event-driven bursts
- Grid #3: Handle extreme volatility

This selection provides a **comprehensive test suite** for spatio-temporal prediction models.

---

**Selection Date**: 2024-12-15  
**Analysis Method**: Feature-based selection with distance constraints (>15 units)
