import os
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

VECTORIZER_PATH = os.path.join(MODEL_DIR, "vectorizer.pkl")
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")

# We use global variables so they load once when the app starts
vectorizer = None
model = None

def load_models():
    global vectorizer, model
    if os.path.exists(VECTORIZER_PATH) and os.path.exists(MODEL_PATH):
        vectorizer = joblib.load(VECTORIZER_PATH)
        model = joblib.load(MODEL_PATH)
    else:
        print("WARNING: Model files not found! Please run train.py first.")
        vectorizer = None
        model = None

# Load the models immediately. Because it's from a .pkl, this is instantly fast.
load_models()

def predict_scam(text):
    if vectorizer is None or model is None:
        # Failsafe if training wasn't done yet, return 0 risk
        return 0, 0.0

    text_vec = vectorizer.transform([text])
    prediction = model.predict(text_vec)[0]
    probability = model.predict_proba(text_vec)[0][1]
    return int(prediction), float(probability)