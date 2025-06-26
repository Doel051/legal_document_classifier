import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

# 1. Load training data
try:
    data = pd.read_csv('legal_docs_dataset.csv')  # Update to your dataset
    texts = data['text'].tolist()
    labels = data['label'].tolist()
except Exception as e:
    print(f"Error loading data: {e}")
    exit()

# 2. Split data
X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.2, random_state=42
)

# 3. Define and train pipeline
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(
        stop_words='english',
        ngram_range=(1, 2)
    )),
    ('clf', LinearSVC(C=0.5, max_iter=2000))
])

print("Training model...")
pipeline.fit(X_train, y_train)

# 4. Evaluate
y_pred = pipeline.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"\nModel accuracy: {accuracy:.2%}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# 5. Save model
joblib.dump(pipeline, 'legal_doc_classifier.pkl')
print("Model saved to legal_doc_classifier.pkl")
