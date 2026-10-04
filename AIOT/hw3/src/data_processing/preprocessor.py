"""
Email preprocessing module for spam classification.
"""
import pandas as pd
import numpy as np
from typing import Tuple, List
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk

class EmailPreprocessor:
    """Email text preprocessing class for spam classification."""
    
    def __init__(self):
        """Initialize the preprocessor with necessary NLTK downloads."""
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet')
            
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.vectorizer = TfidfVectorizer()
        
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess a single email text.
        
        Args:
            text: Raw email text
            
        Returns:
            Preprocessed text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stop words and lemmatize
        tokens = [
            self.lemmatizer.lemmatize(token)
            for token in tokens
            if token not in self.stop_words and token.isalnum()
        ]
        
        return ' '.join(tokens)
    
    def fit_transform(self, texts: List[str]) -> np.ndarray:
        """
        Fit the vectorizer and transform the texts.
        
        Args:
            texts: List of email texts
            
        Returns:
            Feature matrix
        """
        processed_texts = [self.preprocess_text(text) for text in texts]
        return self.vectorizer.fit_transform(processed_texts)
    
    def transform(self, texts: List[str]) -> np.ndarray:
        """
        Transform new texts using the fitted vectorizer.
        
        Args:
            texts: List of email texts
            
        Returns:
            Feature matrix
        """
        processed_texts = [self.preprocess_text(text) for text in texts]
        return self.vectorizer.transform(processed_texts)