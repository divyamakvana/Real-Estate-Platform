import os
import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SALE_MODEL_PATH = os.path.join(BASE_DIR, "sale_price_model.joblib")
RENT_MODEL_PATH = os.path.join(BASE_DIR, "rent_price_model.joblib")

# Load models once
try:
    sale_model = joblib.load(SALE_MODEL_PATH)
    rent_model = joblib.load(RENT_MODEL_PATH)
    print("Models loaded successfully")
except Exception as e:
    print("Error loading models:", e)
    sale_model = rent_model = None

def predict_property_price(data, deal_type='sale'):
    """Return predicted price for a property safely"""
    model = sale_model if deal_type == 'sale' else rent_model
    if model is None:
        raise ValueError("Model not loaded")

    # Numeric features
    numeric_features = {
        'area': float(data.get('area') or 0),
        'bedrooms': float(data.get('bedrooms') or 0),
        'bathrooms': float(data.get('bathrooms') or 0),
        'floor_number': float(data.get('floor_number') or 0),
        'total_floors': float(data.get('total_floors') or 0),
        'parking': float(data.get('parking') or 0)
    }

    # Categorical features
    categorical_features = {
        'bhk': str(data.get('bhk') or 'unknown'),
        'furnishing': str(data.get('furnishing') or 'unknown'),
        'property_type': str(data.get('property_type') or 'unknown'),
        'property_age': str(data.get('property_age') or 'unknown'),
        'facing': str(data.get('facing') or 'unknown'),
        'locality': str(data.get('locality') or 'unknown'),
        'city': str(data.get('city') or 'unknown')
    }

    # Combine and make DataFrame
    X_dict = {**numeric_features, **categorical_features}
    X = pd.DataFrame([X_dict])

    # Ensure column order matches training
    if hasattr(model, 'feature_names_in_'):
        X = X[model.feature_names_in_]

    prediction = model.predict(X)[0]
    return round(prediction, 2)
