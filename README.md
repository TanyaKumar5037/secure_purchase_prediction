# secure_purchase_prediction
A secure machine learning-based web application that predicts customer purchase intent using behavioral analytics, integrated with cryptographic techniques and an interactive dashboard.
# 🛒 Secure Customer Purchase Prediction System

This project is a full-stack machine learning application that predicts whether a customer will purchase a product based on their browsing behavior. The system combines data analytics, machine learning, and cryptographic techniques to ensure both accurate predictions and secure data handling.

Features

- Interactive dashboard with real-time charts
- Machine learning model (Random Forest Classifier)
- Data encryption using AES
- User identity protection using SHA-256 hashing
- Flask-based backend with API support
- Live visualization of customer session behavior

How It Works

1. User inputs session data (e.g., bounce rate, page views, product interactions)
2. Data is processed and converted into model-compatible format
3. Security layer ensures:
   - Encrypted dataset handling
   - Hashed user identifiers
4. The trained ML model predicts purchase intent
5. Result is displayed on an interactive dashboard

Tech Stack

- **Frontend:** HTML, CSS, JavaScript (Chart.js)
- **Backend:** Flask (Python)
- **Machine Learning:** Scikit-learn (Random Forest)
- **Data Processing:** Pandas, NumPy
- **Security:** AES Encryption, SHA-256 Hashing

Security Implementation

- Data is encrypted using Advanced Encryption Standard (AES)
- Sensitive user information is hashed using SHA-256
- Ensures privacy and protection against data exposure

Project Structure

secure_purchase_prediction/
│── templates/
│── model/
│── encrypted_data/
│── app.py
│── train_model.py
│── encryption.py
│── requirements.txt

Installation

```bash
pip install -r requirements.txt
python app.py
