import pandas as pd
from encryption import decrypt_file
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
import pickle
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

decrypt_file()

df = pd.read_csv("data/decrypted.csv")

# Data validation
logger.info(f"Dataset shape: {df.shape}")
logger.info(f"Null values:\n{df.isnull().sum()}")
logger.info(f"Duplicates: {df.duplicated().sum()}")

# Remove nulls
df = df.dropna()

df['Revenue'] = df['Revenue'].map({True: 1, False: 0})

df = pd.get_dummies(df, drop_first=True)

X = df.drop('Revenue', axis=1)
y = df['Revenue']

logger.info(f"Class distribution:\n{y.value_counts()}")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=15)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

# Calculate metrics
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, zero_division=0)
recall = recall_score(y_test, y_pred, zero_division=0)
f1 = f1_score(y_test, y_pred, zero_division=0)
cv_scores = cross_val_score(model, X_train, y_train, cv=5)

metrics = {
    "accuracy": float(accuracy),
    "precision": float(precision),
    "recall": float(recall),
    "f1_score": float(f1),
    "cv_mean": float(cv_scores.mean()),
    "cv_std": float(cv_scores.std()),
    "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
    "feature_count": len(X.columns),
    "training_samples": len(X_train),
    "test_samples": len(X_test)
}

# Save metrics
with open("model/metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)

logger.info(f"Accuracy: {accuracy:.4f}")
logger.info(f"Precision: {precision:.4f}")
logger.info(f"Recall: {recall:.4f}")
logger.info(f"F1-Score: {f1:.4f}")
logger.info(f"CV Scores: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
logger.info("\n" + classification_report(y_test, y_pred))

# Save model
with open("model/model.pkl", "wb") as f:
    pickle.dump(model, f)

logger.info("Model and metrics saved successfully")