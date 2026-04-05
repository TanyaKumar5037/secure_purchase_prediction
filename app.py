from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from encryption import hash_data
from auth import register_user, login_user, logout_user, login_required, get_current_user, init_users
import pickle
import pandas as pd
import logging
import json
import os

app = Flask(__name__)
app.secret_key = "your_secret_key_change_this_in_production"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize users on startup
init_users()

# Load trained model with error handling
model = None
try:
    with open("model/model.pkl", "rb") as f:
        model = pickle.load(f)
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load model: {e}")

# Load metrics with default values
metrics = {
    "accuracy": 0.0,
    "precision": 0.0,
    "recall": 0.0,
    "f1_score": 0.0,
    "cv_mean": 0.0,
    "feature_count": 0,
    "training_samples": 0,
    "test_samples": 0
}

try:
    if os.path.exists("model/metrics.json"):
        with open("model/metrics.json", "r") as f:
            loaded_metrics = json.load(f)
            metrics.update(loaded_metrics)
        logger.info("Metrics loaded successfully")
    else:
        logger.warning("metrics.json not found, using default metrics")
except Exception as e:
    logger.error(f"Failed to load metrics: {e}")


# 🔷 HOME ROUTE (Dashboard UI)
@app.route("/")
def home():
    username = get_current_user()
    if username:
        return render_template("index.html", username=username, metrics=metrics)
    return redirect(url_for("login"))


# 🔷 REGISTER ROUTE
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        
        success, message = register_user(username, password, email)
        
        if success:
            logger.info(f"User {username} registered successfully")
            return redirect(url_for("login"))
        else:
            return render_template("index.html", error=message), 400
    
    return render_template("index.html")


# 🔷 LOGIN ROUTE
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        success, message = login_user(username, password)
        
        if success:
            session["username"] = username
            logger.info(f"User {username} logged in successfully")
            return redirect(url_for("home"))
        else:
            return render_template("index.html", error=message), 401
    
    return render_template("index.html")


# 🔷 LOGOUT ROUTE
@app.route("/logout")
def logout():
    username = session.get("username")
    logout_user()
    logger.info(f"User {username} logged out")
    return redirect(url_for("login"))


# 🔷 HELPER FUNCTION - Unified prediction logic
def make_prediction(data):
    """Process input and return prediction with validation"""
    if model is None:
        return None, "Model not available. Please train the model first."
    
    try:
        # Convert string values to appropriate types
        processed_data = {}
        for key, value in data.items():
            try:
                processed_data[key] = float(value) if value else 0
            except (ValueError, TypeError):
                processed_data[key] = 0
        
        # Hash user ID if present
        if "user_id" in processed_data:
            processed_data["user_id"] = hash_data(str(processed_data["user_id"]))
        
        input_df = pd.DataFrame([processed_data])
        input_df = pd.get_dummies(input_df)
        
        # Align with model features
        model_columns = model.feature_names_in_
        input_df = input_df.reindex(columns=model_columns, fill_value=0)
        
        prediction = model.predict(input_df)[0]
        confidence = model.predict_proba(input_df)[0]
        
        result = "✅ Will Purchase" if prediction == 1 else "❌ Will Not Purchase"
        confidence_pct = max(confidence) * 100
        
        logger.info(f"Prediction: {result} (Confidence: {confidence_pct:.2f}%)")
        return f"{result} (Confidence: {confidence_pct:.1f}%)", None
    
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return None, f"Error in prediction: {str(e)}"


# 🔷 API ROUTE (Postman / JSON) - PROTECTED
@app.route("/predict", methods=["POST"])
@login_required
def predict():
    """Protected API endpoint for predictions"""
    try:
        data = request.json
        result, error = make_prediction(data)
        
        if error:
            return jsonify({"error": error}), 400
        
        username = get_current_user()
        logger.info(f"API prediction made by user: {username}")
        
        return jsonify({"prediction": result}), 200
    except Exception as e:
        logger.error(f"API prediction error: {e}")
        return jsonify({"error": str(e)}), 500


# 🔷 FORM ROUTE (Frontend HTML) - PROTECTED
@app.route("/predict_form", methods=["POST"])
@login_required
def predict_form():
    """Protected form endpoint for predictions"""
    try:
        data = request.form.to_dict()
        result, error = make_prediction(data)
        
        username = get_current_user()
        
        if error:
            logger.error(f"Form prediction error for {username}: {error}")
            return render_template("index.html", 
                                 prediction=None, 
                                 error=error, 
                                 username=username, 
                                 metrics=metrics), 400
        
        logger.info(f"Form prediction made by user: {username}")
        
        return render_template("index.html", 
                             prediction=result, 
                             username=username, 
                             metrics=metrics), 200
    except Exception as e:
        logger.error(f"Form prediction error: {e}")
        username = get_current_user()
        return render_template("index.html", 
                             error=str(e), 
                             username=username, 
                             metrics=metrics), 500


# 🔷 MODEL INFO ENDPOINT - PROTECTED
@app.route("/model_info", methods=["GET"])
@login_required
def model_info():
    """Return model metadata"""
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500
    
    return jsonify({
        "features": list(model.feature_names_in_),
        "feature_count": len(model.feature_names_in_),
        "model_type": type(model).__name__,
        **metrics
    }), 200


# 🔷 HEALTH CHECK
@app.route("/health", methods=["GET"])
def health():
    """Check if app is running"""
    return jsonify({"status": "running"}), 200


if __name__ == "__main__":
    logger.info("Starting Secure Purchase Prediction System...")
    app.run(debug=True, host="127.0.0.1", port=5000)