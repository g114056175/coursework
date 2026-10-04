"""
Visualization utilities for spam classification results.
"""
from typing import Dict, List
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import streamlit as st

class SpamVisualizer:
    """Visualization tools for spam classification results."""
    
    @staticmethod
    def plot_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray) -> None:
        """
        Plot confusion matrix using seaborn.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
        """
        cm = confusion_matrix(y_true, y_pred)
        plt.figure(figsize=(8, 6))
        sns.heatmap(
            cm, 
            annot=True, 
            fmt='d',
            cmap='Blues',
            xticklabels=['Ham', 'Spam'],
            yticklabels=['Ham', 'Spam']
        )
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        st.pyplot(plt)
        plt.close()
        
    @staticmethod
    def plot_metrics(metrics: Dict[str, float]) -> None:
        """
        Plot performance metrics.
        
        Args:
            metrics: Dictionary of metric names and values
        """
        plt.figure(figsize=(10, 6))
        metrics_df = pd.DataFrame(
            list(metrics.items()), 
            columns=['Metric', 'Value']
        )
        sns.barplot(data=metrics_df, x='Metric', y='Value')
        plt.title('Model Performance Metrics')
        plt.ylim(0, 1)
        st.pyplot(plt)
        plt.close()
        
    @staticmethod
    def plot_probability_distribution(probabilities: np.ndarray) -> None:
        """
        Plot probability distribution for predictions.
        
        Args:
            probabilities: Predicted probabilities
        """
        plt.figure(figsize=(10, 6))
        sns.histplot(probabilities[:, 1], bins=50)
        plt.title('Spam Probability Distribution')
        plt.xlabel('Probability of being Spam')
        plt.ylabel('Count')
        st.pyplot(plt)
        plt.close()