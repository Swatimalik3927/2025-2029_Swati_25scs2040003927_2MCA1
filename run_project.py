"""
Master Execution & Launcher Script for Social Media Engagement Metrics System
Based on Swati Kumari's MCA Internship Report at Codec Technologies
"""
import os
import sys
import subprocess
import time

def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title.upper()}")
    print("=" * 70)

def main():
    print_header("Social Media Content Engagement Tracking & Analysis System")
    print("Author Project Basis: Swati Kumari (Roll No: 25scs2040003927)")
    print("Institution: IILM University, Greater Noida | Organization: Codec Technologies")
    print("-" * 70)

    # 1. Run Data Collection
    print_header("Step 1: Live Data Harvesting & Ingestion")
    from src.data_collector import generate_multiplatform_dataset, save_raw_data
    raw_df = generate_multiplatform_dataset(sample_size=400)
    save_raw_data(raw_df)

    # 2. Run ETL Pipeline & Database Creation
    print_header("Step 2: ETL Pipeline & SQLite Database Population")
    from src.etl_pipeline import run_etl
    cleaned_df = run_etl()

    # 3. Run Analytics Engine
    print_header("Step 3: Analytics Suite & Heatmap Matrix Calculation")
    from src.analytics_engine import run_analytics_suite
    analytics = run_analytics_suite(cleaned_df)
    
    kpis = analytics['kpis']
    print(f" -> Total Views Processed: {kpis['total_views']:,}")
    print(f" -> Total Engagements: {kpis['total_likes'] + kpis['total_comments'] + kpis['total_shares']:,}")
    print(f" -> Average Engagement Rate: {kpis['avg_engagement_rate']}%")
    print(f" -> Best Posting Window: {kpis['peak_day']} at {kpis['peak_hour']}")

    # 4. Train ML Predictor
    print_header("Step 4: Machine Learning Model Training (Random Forest)")
    from src.ml_predictor import train_engagement_model
    ml_eval = train_engagement_model(cleaned_df)
    print(f" -> Model Trained: MAE={ml_eval['mae']}, R2 Score={ml_eval['r2_score']}")

    # 5. Launch Interactive BI Dashboard
    print_header("Step 5: Launching Web Interactive BI Dashboard")
    port = 5000
    print(f" -> Starting Flask Dashboard on http://127.0.0.1:{port}")
    print(" -> Press Ctrl+C to stop the dashboard server.")
    print("-" * 70)
    
    from app import app
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    main()
