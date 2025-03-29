from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

app = Flask(__name__)
CORS(app)

# Initialize preprocessing
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

# Global models
models = {
    "logistic": None,
    "random_forest": None
}
vectorizer = TfidfVectorizer(max_features=10)

def clean_text(text):
    """Basic text cleaning"""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\@\w+|\#', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def preprocess_text(text):
    """Tokenization and lemmatization"""
    text = clean_text(text)
    tokens = text.split()
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
    return ' '.join(tokens)

def initialize_models():
    """Initialize models with proper vectorizer setup"""
    global models, vectorizer
    
    print("⚙️ Initializing models...")
    try:
        # Load models
        models["logistic"] = joblib.load('logistic.joblib')
        models["random_forest"] = joblib.load('random_forest.joblib')
        
        # Initialize vectorizer with proper vocabulary
        dummy_texts = [
            "politics government election democracy president",
            "sports football game team player win",
            "technology computer science data machine learning",
            "health medical doctor hospital patient",
            "business market company stock economy"
        ]
        processed_dummies = [preprocess_text(t) for t in dummy_texts]
        vectorizer.fit(processed_dummies)
        
        print("✅ Models initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing models: {e}")
        raise

@app.route('/predict', methods=['POST'])
def predict():
    """Handle prediction requests with dimension matching"""
    data = request.get_json()
    text = data.get('text', '').strip()
    
    if not text or len(text.split()) < 5:
        return jsonify({
            "error": "Invalid input",
            "message": "Text must contain at least 5 words"
        }), 400

    try:
        # Preprocess and vectorize
        processed_text = preprocess_text(text)
        features = vectorizer.transform([processed_text])
        
        # Ensure feature dimensions match
        if features.shape[1] != 5000:
            return jsonify({
                "error": "Feature dimension mismatch",
                "message": f"Expected 5000 features, got {features.shape[1]}"
            }), 500
        
        # Get predictions
        results = {}
        for name, model in models.items():
            try:
                proba = model.predict_proba(features)[0]
                results[name] = {
                    "prediction": "Fake" if proba[1] >= 0.5 else "Real",
                    "confidence": round(float(proba[1] if proba[1] >= 0.5 else 1-proba[1]), 4),
                    "probability": round(float(proba[1]), 4)
                }
            except Exception as e:
                print(f"Model {name} prediction failed: {str(e)}")
                continue
        
        if not results:
            return jsonify({"error": "All model predictions failed"}), 500
        
        # Calculate ensemble prediction
        avg_prob = np.mean([v["probability"] for v in results.values()])
        final_prediction = "Fake" if avg_prob >= 0.5 else "Real"
        
        return jsonify({
            "prediction": final_prediction,
            "confidence": round(float(avg_prob if final_prediction == "Fake" else 1-avg_prob), 4),
            "models": results,
            "processed_text": processed_text[:300] + ("..." if len(processed_text) > 300 else "")
        })
        
    except Exception as e:
        print(f"Prediction error: {str(e)}")
        return jsonify({
            "error": "Prediction failed",
            "message": str(e)
        }), 500

# Initialize on startup
initialize_models()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)