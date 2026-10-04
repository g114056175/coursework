"""
Spam email classifier implementation.
"""
from typing import Tuple, Dict, Any
import numpy as np
from sklearn.base import BaseEstimator
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

class SpamClassifier:
    """Spam email classifier with evaluation metrics."""
    
    def __init__(self, model: BaseEstimator = None):
        """
        Initialize the classifier.
        
        Args:
            model: Sklearn classifier (defaults to MultinomialNB if None)
        """
        self.model = model if model is not None else MultinomialNB()
        
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Train the classifier.
        
        Args:
            X: Feature matrix
            y: Target labels (0 for ham, 1 for spam)
        """
        self.model.fit(X, y)
        
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict spam/ham labels for new emails.
        
        Args:
            X: Feature matrix
            
        Returns:
            Predicted labels
        """
        return self.model.predict(X)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Get probability estimates.
        
        Args:
            X: Feature matrix
            
        Returns:
            Probability estimates for each class
        """
        return self.model.predict_proba(X)
    
    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """
        Evaluate the model performance.
        
        Args:
            X: Feature matrix
            y: True labels
            
        Returns:
            Dictionary with performance metrics
        """
        y_pred = self.predict(X)
        return {
            'accuracy': accuracy_score(y, y_pred),
            'precision': precision_score(y, y_pred),
            'recall': recall_score(y, y_pred),
            'f1': f1_score(y, y_pred)
        }