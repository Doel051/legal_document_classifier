# classifier.py
import joblib
import os

# Load the model once at module load
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'legal_doc_classifier.pkl')
pipeline = joblib.load(MODEL_PATH)

def classify_document(text):
    """
    Classify a legal document using a TF-IDF + LinearSVC pipeline.
    Returns one of: 'contract', 'court_filing', 'm&a_agreement', or 'unknown'.
    """
    pred = pipeline.predict([text])
    return pred[0]
