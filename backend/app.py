import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import whois
from urllib.parse import urlparse
from datetime import datetime
import sqlite3
from model import predict_scam

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "scans.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS scans
                 (text TEXT, score INTEGER, risk TEXT, ml REAL)""")
    conn.commit()
    conn.close()

def save_scan(text, score, risk, ml):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO scans VALUES (?,?,?,?)", (text, score, risk, ml))
    conn.commit()
    conn.close()

init_db()

def get_domain_age(domain):
    # Render's free tier blocks port 43 (WHOIS), which causes the request to timeout and crash.
    # To fix this, we bypass whois lookup if running on Render (where PORT env var is usually set).
    if os.environ.get("RENDER"):
        return -1
        
    try:
        domain_info = whois.whois(domain)
        creation_date = domain_info.creation_date

        if not creation_date:
            return None

        if isinstance(creation_date, list):
            creation_date = creation_date[0]

        age_days = (datetime.now() - creation_date).days
        return age_days
    except:
        return -1

def extract_domain(text):
    urls = re.findall(r'(https?://[^\s]+)', text)
    if urls:
        parsed_url = urlparse(urls[0])
        return parsed_url.netloc
    return None

def analyze_text(text):
    text_lower = text.lower()
    score = 0
    reasons = []

    scam_keywords = [
        "win money", "earn fast", "urgent", "limited offer",
        "click now", "free", "guaranteed", "no experience",
        "work from home", "investment", "double your money"
    ]

    for word in scam_keywords:
        if word in text_lower:
            score += 10
            reasons.append(f"Keyword detected: {word}")

    if re.search(r"http[s]?://", text):
        score += 30
        reasons.append("Contains a link")

        domain = extract_domain(text)

        if domain:
            age = get_domain_age(domain)

            if age == -1:
                score += 35
                reasons.append("Suspicious domain (WHOIS lookup failed)")
            elif age is None:
                score += 35
                reasons.append("Suspicious domain (hidden or unverifiable)")
            elif age < 30:
                score += 30
                reasons.append(f"Very new domain ({age} days old)")
            elif age < 180:
                score += 15
                reasons.append(f"New domain ({age} days old)")
            else:
                reasons.append(f"Old domain ({age} days old)")

    if re.search(r"\d{10,}", text):
        score += 10
        reasons.append("Suspicious number pattern")

    if text.isupper():
        score += 10
        reasons.append("All caps text")

    if len(text) < 10:
        score += 5
        reasons.append("Very short message")

    return score, reasons

@app.route("/")
def home():
    return "Server is running"

@app.route("/scan", methods=["POST"])
def scan():
    data = request.get_json()
    text = data.get("text", "")

    score, reasons = analyze_text(text)

    prediction, probability = predict_scam(text)

    if prediction == 1:
        score += int(probability * 30)
        reasons.append(f"ML model detected scam ({round(probability*100,2)}%)")

    if probability > 0.6:
        score += 20
        reasons.append("High ML confidence boost")

    if score > 100:
        score = 100

    if score >= 50:
        risk = "High"
    elif score >= 25:
        risk = "Medium"
    else:
        risk = "Low"

    save_scan(text, score, risk, probability)

    return jsonify({
        "score": score,
        "risk": risk,
        "reasons": reasons,
        "ml_confidence": round(probability * 100, 2)
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)