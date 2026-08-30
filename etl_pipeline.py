import os
import sqlite3
import pandas as pd
import numpy as np

DB_PATH = "data/social_media_engagement.db"
RAW_CSV_PATH = "data/raw_engagement_data.csv"
CLEANED_CSV_PATH = "data/cleaned_engagement_data.csv"

DAYS_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def clean_and_transform(df):
    """
    Cleans raw engagement data, calculates engagement rates, and extracts time features.
    """
    df = df.copy()
    
    # 1. Fill missing numeric & string values
    df['views'] = pd.to_numeric(df['views'], errors='coerce').fillna(0).astype(int)
    df['likes'] = pd.to_numeric(df['likes'], errors='coerce').fillna(0).astype(int)
    df['comments'] = pd.to_numeric(df['comments'], errors='coerce').fillna(0).astype(int)
    df['shares'] = pd.to_numeric(df['shares'], errors='coerce').fillna(0).astype(int)
    df['impressions'] = pd.to_numeric(df['impressions'], errors='coerce').fillna(df['views']).astype(int)
    df['thumbnail_url'] = df.get('thumbnail_url', "https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?w=500").fillna("https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?w=500")
    
    # 2. Datetime parsing & feature engineering
    df['published_at'] = pd.to_datetime(df['published_at'], errors='coerce')
    df['published_at'] = df['published_at'].fillna(pd.Timestamp.now())
    
    df['posting_hour'] = df['published_at'].dt.hour
    df['day_of_week'] = df['published_at'].dt.day_name()
    df['day_index'] = df['published_at'].dt.dayofweek
    df['year_month'] = df['published_at'].dt.strftime('%Y-%m')
    
    # 3. Time slot classification
    def get_time_slot(hour):
        if 6 <= hour < 12:
            return "Morning (6 AM - 12 PM)"
        elif 12 <= hour < 17:
            return "Afternoon (12 PM - 5 PM)"
        elif 17 <= hour < 22:
            return "Evening (5 PM - 10 PM)"
        else:
            return "Night (10 PM - 6 AM)"
            
    df['posting_slot'] = df['posting_hour'].apply(get_time_slot)
    
    # 4. Engagement metrics
    df['total_engagements'] = df['likes'] + df['comments'] + df['shares']
    
    # Engagement Rate (%) = (Total Engagements / Views) * 100
    df['engagement_rate'] = np.where(
        df['views'] > 0,
        (df['total_engagements'] / df['views']) * 100,
        (df['total_engagements'] / df['impressions'].replace(0, 1)) * 100
    )
    df['engagement_rate'] = df['engagement_rate'].round(2)
    
    # Ratios
    df['like_to_view_pct'] = np.where(df['views'] > 0, (df['likes'] / df['views']) * 100, 0).round(2)
    df['comment_to_view_pct'] = np.where(df['views'] > 0, (df['comments'] / df['views']) * 100, 0).round(2)
    df['share_to_view_pct'] = np.where(df['views'] > 0, (df['shares'] / df['views']) * 100, 0).round(2)
    
    # Virality Tier
    q75 = df['engagement_rate'].quantile(0.75)
    q25 = df['engagement_rate'].quantile(0.25)
    
    def get_tier(er):
        if er >= q75:
            return "🔥 Viral Boom"
        elif er >= q25:
            return "⚡ Solid Reach"
        else:
            return "🌱 Steady Growth"
            
    df['performance_tier'] = df['engagement_rate'].apply(get_tier)
    
    return df

def load_into_sqlite(df, db_path=DB_PATH):
    """
    Saves cleaned dataframe and aggregated views into SQLite database tables.
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    
    # 1. Main Posts Table
    df_sql = df.copy()
    df_sql['published_at'] = df_sql['published_at'].astype(str)
    df_sql.to_sql('posts', conn, if_exists='replace', index=False)
    
    # 2. Hourly Posting Analytics Table
    hourly_df = df.groupby(['day_of_week', 'posting_hour']).agg(
        avg_engagement_rate=('engagement_rate', 'mean'),
        avg_views=('views', 'mean'),
        avg_likes=('likes', 'mean'),
        post_count=('post_id', 'count')
    ).reset_index().round(2)
    hourly_df.to_sql('hourly_analytics', conn, if_exists='replace', index=False)
    
    # 3. Format Analytics Table
    format_df = df.groupby(['platform', 'format_type']).agg(
        total_posts=('post_id', 'count'),
        avg_views=('views', 'mean'),
        avg_likes=('likes', 'mean'),
        avg_comments=('comments', 'mean'),
        avg_shares=('shares', 'mean'),
        avg_engagement_rate=('engagement_rate', 'mean')
    ).reset_index().round(2)
    format_df.to_sql('format_analytics', conn, if_exists='replace', index=False)
    
    conn.close()
    print(f"[ETL] Saved SQLite database tables to '{db_path}'")

def run_etl(raw_csv_path=RAW_CSV_PATH, cleaned_csv_path=CLEANED_CSV_PATH, db_path=DB_PATH):
    if not os.path.exists(raw_csv_path):
        from src.data_collector import generate_multiplatform_dataset, save_raw_data
        raw_df = generate_multiplatform_dataset()
        save_raw_data(raw_df, raw_csv_path)
    else:
        raw_df = pd.read_csv(raw_csv_path)
        
    print("[ETL] Transforming engagement metrics and thumbnails...")
    cleaned_df = clean_and_transform(raw_df)
    
    os.makedirs(os.path.dirname(cleaned_csv_path), exist_ok=True)
    cleaned_df.to_csv(cleaned_csv_path, index=False)
    print(f"[ETL] Cleaned dataset exported to '{cleaned_csv_path}' ({len(cleaned_df)} rows)")
    
    load_into_sqlite(cleaned_df, db_path)
    return cleaned_df

if __name__ == "__main__":
    df = run_etl()
