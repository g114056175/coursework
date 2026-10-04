# AIOT_hw3 - Spam Email Classification System

This project implements an intelligent email spam classification system using machine learning techniques. Built as part of the AIOT (Artificial Intelligence of Things) course homework 3, it demonstrates the practical application of Natural Language Processing (NLP) and machine learning in cybersecurity.

## Live Demo
Experience the application here: [Streamlit Cloud Demo](https://aiothw3-jycxbyewety9g3fogipmeq.streamlit.app/)

## Project Overview
The system uses TF-IDF (Term Frequency-Inverse Document Frequency) vectorization and Naive Bayes classification to analyze email content and determine whether it's spam or legitimate (ham). The model is trained on a comprehensive SMS spam dataset and achieves high accuracy in classification.

## Key Features
- **Intelligent Spam Detection**: Uses machine learning to classify emails
- **Real-time Analysis**: Instant classification of input text
- **Probability Visualization**: Shows classification confidence with an interactive bar chart
- **Keyword Analysis**: Identifies influential words affecting the classification
- **Model Performance Metrics**: Displays accuracy, precision, recall, and F1 score
- **Interactive Web Interface**: User-friendly Streamlit application
- **Confusion Matrix**: Visual representation of model performance

## Implementation Details

### Machine Learning Pipeline
1. **Data Processing**
   - TF-IDF Vectorization for text feature extraction
   - Text normalization and preprocessing
   - Feature selection for optimal performance

2. **Model Architecture**
   - Naive Bayes classifier for spam detection
   - Probability-based classification
   - Feature importance analysis

3. **Performance Evaluation**
   - Cross-validation for model validation
   - Comprehensive metrics calculation
   - Confusion matrix visualization

### Project Structure
```
.
├── streamlit_app.py    # Main application file
├── sms_spam.csv       # Training dataset
├── requirements.txt   # Project dependencies
├── README.md         # Project documentation
└── .gitignore       # Git ignore file
```

## Usage Guide
1. Visit the [live demo](https://aiothw3-jycxbyewety9g3fogipmeq.streamlit.app/)

2. **Demo Page**
   - Select a sample email from the dropdown menu
   - Edit or enter your own text in the input area
   - Click "Analyze" to get instant classification results
   - View the probability visualization
   - Check influential keywords in your text

3. **Performance Page**
   - Review model accuracy metrics
   - Examine precision and recall scores
   - Study the confusion matrix
   - Understand model effectiveness

## Technical Stack
- **Python**: Core programming language
- **Streamlit**: Web application framework
- **scikit-learn**: Machine learning library
  - TfidfVectorizer for text processing
  - MultinomialNB for classification
- **pandas**: Data manipulation
- **matplotlib & seaborn**: Data visualization
- **NumPy**: Numerical computations

## Local Development Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/g114056175/AIOT_hw3.git
   cd AIOT_hw3
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run streamlit_app.py
   ```

## References & Resources
- **Dataset Source**: SMS Spam Collection from [Hands-On-Artificial-Intelligence-for-Cybersecurity](https://github.com/PacktPublishing/Hands-On-Artificial-Intelligence-for-Cybersecurity)
- **Algorithm Background**: [Naive Bayes for Text Classification](https://scikit-learn.org/stable/modules/naive_bayes.html)
- **Development Tools**: VS Code, GitHub, Streamlit Cloud
- **Streamlit Deployment**: Custom deployment on Streamlit Cloud platform