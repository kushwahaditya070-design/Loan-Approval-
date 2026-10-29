from flask import Flask, render_template, request, jsonify
from pathlib import Path
import joblib
import pandas as pd
import numpy as np

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model" / "loan_model.pkl"

# The supplied model was saved with scikit-learn 1.6.1.
# Install the versions in requirements.txt before loading the model.
model = joblib.load(MODEL_PATH)

# Exact selected features supplied by the user. Keep this order aligned with training.
DEFAULT_FEATURES = [
    "Gender", "Married", "Education", "ApplicantIncome", "LoanAmount", "Property_Area"
]

model_features = getattr(model, "feature_names_in_", None)
FEATURES = list(model_features) if model_features is not None else DEFAULT_FEATURES

ALIASES = {
    "Gender": ["Gender", "gender"],
    "Married": ["Married", "Marital Status", "married"],
    "Education": ["Education", "education"],
    "ApplicantIncome": ["ApplicantIncome", "Applicant Income", "Applicant Income (₹)", "applicant_income"],
    "LoanAmount": ["LoanAmount", "Loan Amount", "Loan Amount (₹)", "loan_amount"],
    "Property_Area": ["Property_Area", "Property Area", "property_area"],
}
DEFAULTS = {
    "Gender": "Male", "Married": "No", "Education": "Graduate",
    "ApplicantIncome": 0, "LoanAmount": 0, "Property_Area": "Urban",
}

def find_value(payload, feature):
    candidates = ALIASES.get(feature, [feature, feature.replace("_", " ")])
    for key in candidates:
        if key in payload:
            return payload[key]
    # Case-insensitive fallback
    lower_payload = {str(k).lower(): v for k, v in payload.items()}
    for key in candidates:
        if key.lower() in lower_payload:
            return lower_payload[key.lower()]
    return DEFAULTS.get(feature, 0)

def prepare_row(payload):
    row = {}
    for feature in FEATURES:
        value = find_value(payload, feature)
        # Keep categorical values as strings; cast numerical features to numbers.
        if feature in ["ApplicantIncome", "LoanAmount"]:
            try:
                value = float(value) if value not in ("", None) else DEFAULTS.get(feature, 0)
            except (ValueError, TypeError):
                raise ValueError(f"Please enter a valid number for {feature.replace('_', ' ')}.")
        row[feature] = value
    return pd.DataFrame([row], columns=FEATURES)

def label_prediction(prediction):
    value = str(prediction).strip().lower()
    if value in {"1", "y", "yes", "approved", "true"} or "approv" in value:
        return "Approved"
    if value in {"0", "n", "no", "rejected", "false"} or "reject" in value:
        return "Rejected"
    # Preserve unusual model class labels rather than silently changing meaning.
    return str(prediction)

@app.get("/")
def home():
    return render_template("index.html", features=FEATURES)

@app.get("/api/health")
def health():
    return jsonify({"ok": True, "model_loaded": model is not None, "features": FEATURES})

@app.post("/api/predict")
def predict():
    payload = request.get_json(silent=True) or request.form.to_dict()
    try:
        row = prepare_row(payload)
        raw_prediction = model.predict(row)[0]
        prediction = label_prediction(raw_prediction)
        probability = None
        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(row)[0]
            classes = list(getattr(model, "classes_", []))
            if len(probabilities):
                # If class labels exist, report the probability of the predicted class.
                idx = classes.index(raw_prediction) if raw_prediction in classes else int(np.argmax(probabilities))
                probability = round(float(probabilities[idx]) * 100, 1)
        return jsonify({
            "success": True,
            "prediction": prediction,
            "probability": probability,
            "probability_supported": probability is not None
        })
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except Exception as exc:
        app.logger.exception("Prediction failed")
        return jsonify({
            "success": False,
            "error": "The model could not process these inputs. Check app.py FEATURES and the model's training columns."
        }), 500

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
