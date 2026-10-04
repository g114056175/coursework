# Project Context

## Purpose
This project focuses on spatial-temporal data analysis using deep learning models, specifically ST-ResNet (Spatio-Temporal Residual Networks) for prediction and evaluation tasks. The goal is to train, evaluate, and analyze ST-ResNet models on time-series spatial data to generate performance metrics and visualization heatmaps.

## Tech Stack
- **Language**: Python 3.x
- **Deep Learning**: PyTorch (for ST-ResNet model implementation)
- **Data Processing**: NumPy, Pandas
- **Visualization**: Matplotlib, Seaborn (for heatmaps and prediction visualizations)
- **Data**: CSV format (e.g., `data1.csv` - 149 MB dataset)

## Project Conventions

### Code Style
- Python scripts follow numeric naming convention for sequential execution (e.g., `10_evaluate_stresnet.py`)
- Use descriptive variable names for model components and data structures
- Preference for functional programming patterns in data processing pipelines

### Architecture Patterns
- **Model Architecture**: ST-ResNet with residual connections for spatial-temporal prediction
- **Data Pipeline**: CSV → Preprocessing → Model Training → Evaluation → Visualization
- **Output Structure**: Results organized in dedicated directories (e.g., `new_stresnet_results/`)
- Separation of concerns: separate scripts for training vs. evaluation

### Testing Strategy
- Model evaluation through quantitative metrics: MAE (Mean Absolute Error), MaxAE (Maximum Absolute Error)
- Visualization-based validation: heatmaps comparing predictions vs. ground truth
- Focus on high-change areas and maximum error regions for quality assessment

### Git Workflow
- Not yet defined (to be established based on team preferences)

## Domain Context
**Spatio-Temporal Analysis**: The project deals with data that has both spatial (location-based) and temporal (time-based) dimensions. ST-ResNet is designed to capture patterns across both dimensions simultaneously.

**Key Concepts**:
- **Residual Networks**: Deep learning architecture that helps with gradient flow in very deep networks
- **Heatmap Visualization**: Visual representation of prediction accuracy across spatial regions
- **High-Change Areas**: Regions where the temporal variance is significant, requiring more model attention
- **Ground Truth Comparison**: Evaluating model predictions against actual observed data

## Important Constraints
- Large dataset size (149 MB CSV) requires efficient memory management
- Model evaluation needs to balance computational cost with visualization quality
- Results must be interpretable through both metrics and visualizations

## External Dependencies
- PyTorch ecosystem for deep learning model development and training
- Scientific Python stack (NumPy, Pandas, Matplotlib) for data manipulation and visualization
- Potential GPU dependencies for model training/evaluation (to be confirmed)
