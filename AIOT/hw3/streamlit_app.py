"""
Streamlit application for spam email classification.
Data source: https://github.com/PacktPublishing/Hands-On-Artificial-Intelligence-for-Cybersecurity
"""
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# Sample emails for quick testing
SAMPLE_EMAILS = {
    "None": "",
    "Normal Email 1": "Hi team, The project timeline has been updated. Please review the attached schedule and let me know if you have any conflicts with the proposed deadlines.",
    "Normal Email 2": "Dear Mr. Johnson, Thank you for your interest in our services. I've attached the detailed proposal as discussed. Please feel free to contact me with any questions.",
    "Spam Email 1": "$$$ MAKE MONEY FAST!!! Work from home and earn $10,000/week! 100% GUARANTEED! No experience needed! CLICK NOW to start earning!!!",
    "Spam Email 2": "Congratulations! You have won a prize. Claim now.\n\nDear Lucky Winner,\n\nYou have been selected to receive our exclusive prize worth $1,000! Act fast - this is a limited time offer!\n\nClick here to claim: www.totally-legitimate-prizes.com\nOr call now: 1-800-PRIZE-NOW\n\nHurry! This offer expires in 24 hours.\nNo purchase necessary. Don't miss out!"
}

# Load training data
@st.cache_data
def load_training_data():
    try:
        # Read the SMS spam dataset
        df = pd.read_csv('sms_spam.csv', names=['label', 'text'])
        # Convert ham/spam to 0/1
        df['label'] = (df['label'] == 'spam').astype(int)
        return df['text'].tolist(), df['label'].tolist()
    except Exception as e:
        st.error(f"Error loading dataset: {str(e)}")
        # Fallback to minimal dataset if file loading fails
        emails = [
            "Your account statement is ready",
            "Meeting tomorrow at 10 AM",
            "Win million dollars now!!!",
            "90% OFF luxury watches!!!"
        ]
        labels = [0, 0, 1, 1]
        return emails, labels

def train_and_evaluate_model(emails, labels):
    # Split the dataset
    X_train, X_test, y_train, y_test = train_test_split(emails, labels, test_size=0.2, random_state=42)
    
    # Initialize and fit the vectorizer
    vectorizer = TfidfVectorizer(max_features=1000)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    # Train the model
    model = MultinomialNB()
    model.fit(X_train_vec, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test_vec)
    
    # Calculate metrics
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1': f1_score(y_test, y_pred)
    }
    
    # Calculate confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    
    return vectorizer, model, metrics, cm, (X_test, y_test, y_pred)

def plot_probability_bar(probability):
    fig, ax = plt.subplots(figsize=(10, 2))
    colors = ['green' if probability < 0.5 else 'red']
    sns.barplot(x=[probability], y=['Probability'], ax=ax, palette=colors)
    ax.set_xlim(0, 1)
    plt.title('Spam Classification Probability')
    st.pyplot(fig)
    plt.close()

def plot_confusion_matrix(cm):
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    st.pyplot(fig)
    plt.close()

def show_demo(vectorizer, model):
    # Create a layout with two columns
    col1, col2 = st.columns([1, 3])
    
    # Sample selection in first column
    with col1:
        email_template = st.selectbox(
            "Select template",
            list(SAMPLE_EMAILS.keys())
        )
    
    # Text input in second column
    with col2:
        text_to_analyze = st.text_area(
            "Email content to analyze",
            value=SAMPLE_EMAILS[email_template],
            height=200
        )
    
    if st.button('Analyze') and text_to_analyze:
        # Feature extraction and prediction
        X_test = vectorizer.transform([text_to_analyze])
        spam_prob = model.predict_proba(X_test)[0][1]
        
        # Display results
        st.header('Analysis Results')
        result = "Spam" if spam_prob > 0.5 else "Ham"
        st.write(f"This email is likely: **{result}**")
        
        # Show probability bar
        plot_probability_bar(spam_prob)
        
        # Show detailed probabilities
        st.write(f"- Ham probability: {(1-spam_prob)*100:.2f}%")
        st.write(f"- Spam probability: {spam_prob*100:.2f}%")
        
        # Get words from current text
        current_text_features = vectorizer.transform([text_to_analyze])
        current_words = set()
        for idx, val in enumerate(current_text_features.toarray()[0]):
            if val > 0:
                current_words.add(vectorizer.get_feature_names_out()[idx])
        
        # Calculate feature importance
        feature_importance = pd.DataFrame({
            'word': vectorizer.get_feature_names_out(),
            'importance': model.feature_log_prob_[1] - model.feature_log_prob_[0]
        })
        
        # Only keep words that appear in current text
        feature_importance = feature_importance[feature_importance['word'].isin(current_words)]
        top_features = feature_importance.nlargest(5, 'importance')
        
        st.subheader('Key words influencing the decision')
        if not top_features.empty:
            for _, row in top_features.iterrows():
                st.write(f"- {row['word']}: {row['importance']:.4f}")
        else:
            st.write("No significant keywords found in the text")

def show_model_metrics(metrics, cm):
    st.header('Model Performance Metrics')
    
    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Accuracy", value=f"{metrics['accuracy']:.2%}")
    with col2:
        st.metric(label="Precision", value=f"{metrics['precision']:.2%}")
    with col3:
        st.metric(label="Recall", value=f"{metrics['recall']:.2%}")
    with col4:
        st.metric(label="F1 Score", value=f"{metrics['f1']:.2%}")
    
    # Display confusion matrix
    st.subheader('Confusion Matrix')
    plot_confusion_matrix(cm)

def main():
    st.title('Email Spam Classification System')
    
    # Load and train model
    emails, labels = load_training_data()
    vectorizer, model, metrics, cm, eval_data = train_and_evaluate_model(emails, labels)
    
    # Create sidebar for navigation
    page = st.sidebar.radio("Navigation", ["Spam Detection Demo", "Model Performance"])
    
    # Display appropriate page based on selection
    if page == "Spam Detection Demo":
        show_demo(vectorizer, model)
    else:
        show_model_metrics(metrics, cm)

if __name__ == '__main__':
    main()