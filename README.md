# LoanFlow — Loan Approval Prediction

A responsive HTML/CSS/JavaScript frontend connected to a Flask API and your uploaded `best_model.pkl`.

## 1. Setup (Windows PowerShell)

Open PowerShell in this extracted `loan-approval` folder.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

If PowerShell blocks activation, run this for the current terminal only, then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Open **http://127.0.0.1:5000** in your browser.

## 2. Included files

- `app.py` — Flask routes, loads the saved model, validates input, returns predictions and optional probability.
- `model/loan_model.pkl` — the model you uploaded, copied into this project.
- `templates/index.html` — dashboard and application form.
- `static/style.css` — responsive design and styling.
- `static/script.js` — form submission, API request, and result rendering.

## 3. Important: match the model's training features

The form uses the six selected Loan Prediction fields:
`Gender`, `Married`, `Education`, `ApplicantIncome`, `LoanAmount`, `Property_Area`.

The backend uses `model.feature_names_in_` automatically if the saved model exposes it. Otherwise it falls back to the list above. **These names, order, and value encodings must match the columns used to train your model.** If your training notebook used a different feature list, edit `DEFAULT_FEATURES` and the `ALIASES`/`DEFAULTS` mappings in `app.py`, and adjust the form options in `templates/index.html` to match.

Some pickled scikit-learn models require the exact or compatible scikit-learn version used when saving them. This project pins scikit-learn 1.6.1 because the supplied model metadata indicated that version. If loading fails, share the full traceback and the training environment's package versions.

## 4. API

- `GET /api/health` — checks server/model status and lists feature names.
- `POST /api/predict` — JSON body with the form values; returns `prediction` and probability when `predict_proba` is supported.

## 5. Responsible use

This is a demonstration interface. A model prediction is not a loan approval guarantee and should not be used as the sole basis for a real lending decision. Run locally for development; do not expose the Flask debug server to the public internet.
