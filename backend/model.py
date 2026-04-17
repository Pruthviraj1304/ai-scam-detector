import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
data = pd.read_csv(os.path.join(BASE_DIR, "dataset", "scam_data.csv"))

X = data["text"]
y = data["label"]

vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english', max_features=5000)
X_vec = vectorizer.fit_transform(X)

model = LogisticRegression(max_iter=1000, class_weight='balanced')
model.fit(X_vec, y)

def predict_scam(text):
    text_vec = vectorizer.transform([text])
    prediction = model.predict(text_vec)[0]
    probability = model.predict_proba(text_vec)[0][1]
    return int(prediction), float(probability)