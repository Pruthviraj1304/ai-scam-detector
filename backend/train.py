import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "dataset", "scam_data.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")

print("Initializing AI Model Training...")

# Create models directory if it doesn't exist
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)

# Ensure the dataset exists
if not os.path.exists(DATA_PATH):
    print(f"ERROR: Dataset not found at {DATA_PATH}")
    print("Please make sure your 50MB CSV is placed there with 'text' and 'label' columns.")
    exit(1)

# 1. Load Data
print(f"Loading data from {DATA_PATH}...")
data = pd.read_csv(DATA_PATH)

if 'text' not in data.columns or 'label' not in data.columns:
    print("ERROR: CSV must contain 'text' and 'label' columns.")
    exit(1)

# Drop any empty rows that might crash the vectorizer
data = data.dropna(subset=['text', 'label'])
X = data["text"]
y = data["label"].astype(int)

print(f"Successfully loaded {len(data)} examples.")

# 2. Vectorization
print("Vectorizing text data (this may take a minute for large datasets)...")
vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english', max_features=10000)
X_vec = vectorizer.fit_transform(X)

# 3. Model Training
print("Training Logistic Regression Model...")
model = LogisticRegression(max_iter=1000, class_weight='balanced')
model.fit(X_vec, y)
print("Model training complete!")

# 4. Save to Disk
print("Saving model and vectorizer to disk...")
joblib.dump(vectorizer, os.path.join(MODEL_DIR, "vectorizer.pkl"))
joblib.dump(model, os.path.join(MODEL_DIR, "model.pkl"))

print("DONE! Your highly scalable AI has been saved as .pkl files.")
print("The backend app will now start instantly and use very little RAM.")
