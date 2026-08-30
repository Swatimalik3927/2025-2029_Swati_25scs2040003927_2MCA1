import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

MODEL_FILE = "data/engagement_model.pkl"

def build_model_pipeline():
    """
    Creates feature preprocessing and Random Forest regression pipeline.
    """
    categorical_features = ['platform', 'category', 'format_type', 'day_of_week']
    numeric_features = ['posting_hour', 'title_length']
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features),
            ('num', 'passthrough', numeric_features)
        ]
    )
    
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10))
    ])
    
    return pipeline

def train_engagement_model(df=None, save_path=MODEL_FILE):
    """
    Trains engagement prediction model on processed dataset.
    """
    if df is None:
        if os.path.exists("data/cleaned_engagement_data.csv"):
            df = pd.read_csv("data/cleaned_engagement_data.csv")
        else:
            from src.etl_pipeline import run_etl
            df = run_etl()
            
    df = df.copy()
    df['title_length'] = df['title'].fillna("").apply(len)
    
    features = ['platform', 'category', 'format_type', 'day_of_week', 'posting_hour', 'title_length']
    target = 'engagement_rate'
    
    X = df[features]
    y = df[target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    pipeline = build_model_pipeline()
    pipeline.fit(X_train, y_train)
    
    y_pred = pipeline.predict(X_test)
    mae = round(float(mean_absolute_error(y_test, y_pred)), 2)
    r2 = round(float(r2_score(y_test, y_pred)), 2)
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    joblib.dump(pipeline, save_path)
    
    print(f"[MLPredictor] Model trained & saved to '{save_path}' (MAE: {mae}, R2 Score: {r2})")
    
    return {
        "mae": mae,
        "r2_score": r2,
        "train_samples": len(X_train),
        "test_samples": len(X_test)
    }

def predict_post_engagement(platform, category, format_type, posting_hour, day_of_week, title="", model_path=MODEL_FILE):
    """
    Predicts expected engagement rate (%) for a planned social media post.
    """
    if not os.path.exists(model_path):
        train_engagement_model(save_path=model_path)
        
    pipeline = joblib.load(model_path)
    
    input_df = pd.DataFrame([{
        'platform': platform,
        'category': category,
        'format_type': format_type,
        'day_of_week': day_of_week,
        'posting_hour': int(posting_hour),
        'title_length': len(title)
    }])
    
    predicted_er = float(pipeline.predict(input_df)[0])
    predicted_er = max(0.5, round(predicted_er, 2))
    
    # Assess performance level
    if predicted_er >= 8.0:
        recommendation = "Excellent predicted engagement! High potential to go viral."
        grade = "A+"
    elif predicted_er >= 5.0:
        recommendation = "Good engagement expected. Standard high-performing post."
        grade = "B+"
    else:
        recommendation = "Moderate engagement predicted. Consider posting during peak slots (18:00 - 21:00)."
        grade = "C"
        
    return {
        "predicted_engagement_rate": predicted_er,
        "grade": grade,
        "recommendation": recommendation,
        "input": {
            "platform": platform,
            "category": category,
            "format_type": format_type,
            "day_of_week": day_of_week,
            "posting_hour": posting_hour
        }
    }

if __name__ == "__main__":
    stats = train_engagement_model()
    print("Training Evaluation:", stats)
    pred = predict_post_engagement("YouTube", "Tech", "YouTube Short", 19, "Wednesday", "Amazing AI Tech Breakthrough!")
    print("\nSample Prediction:", pred)
