import os
import sqlite3
import pandas as pd
import numpy as np

DB_PATH = "data/social_media_engagement.db"
DAYS_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def get_db_connection(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def calculate_kpis(df):
    """
    Computes top-level key performance indicators.
    """
    total_posts = int(len(df))
    total_views = int(df['views'].sum())
    total_likes = int(df['likes'].sum())
    total_comments = int(df['comments'].sum())
    total_shares = int(df['shares'].sum())
    avg_engagement_rate = float(round(df['engagement_rate'].mean(), 2))
    
    # Top performing post
    top_post_row = df.loc[df['engagement_rate'].idxmax()] if not df.empty else {}
    top_post = {
        "title": top_post_row.get("title", "N/A"),
        "platform": top_post_row.get("platform", "N/A"),
        "engagement_rate": float(top_post_row.get("engagement_rate", 0)),
        "views": int(top_post_row.get("views", 0)),
        "likes": int(top_post_row.get("likes", 0))
    }
    
    # Peak day & hour
    day_stats = df.groupby('day_of_week')['engagement_rate'].mean()
    peak_day = str(day_stats.idxmax()) if not day_stats.empty else "N/A"
    
    hour_stats = df.groupby('posting_hour')['engagement_rate'].mean()
    peak_hour = int(hour_stats.idxmax()) if not hour_stats.empty else 0
    
    return {
        "total_posts": total_posts,
        "total_views": total_views,
        "total_likes": total_likes,
        "total_comments": total_comments,
        "total_shares": total_shares,
        "avg_engagement_rate": avg_engagement_rate,
        "peak_day": peak_day,
        "peak_hour": f"{peak_hour:02d}:00",
        "top_post": top_post
    }

def generate_posting_heatmap(df):
    """
    Creates a complete 7-day x 24-hour matrix of average engagement rates.
    """
    # Create empty full matrix template
    matrix = pd.DataFrame(0.0, index=DAYS_ORDER, columns=list(range(24)))
    
    grouped = df.groupby(['day_of_week', 'posting_hour'])['engagement_rate'].mean().unstack(level=1)
    
    for day in DAYS_ORDER:
        if day in grouped.index:
            for hour in range(24):
                if hour in grouped.columns and not np.isnan(grouped.loc[day, hour]):
                    matrix.loc[day, hour] = round(float(grouped.loc[day, hour]), 2)
                    
    return matrix

def get_best_posting_slots(df, top_n=5):
    """
    Identifies top N day/hour posting combinations for highest engagement.
    """
    grouped = df.groupby(['day_of_week', 'posting_hour', 'posting_slot']).agg(
        avg_engagement_rate=('engagement_rate', 'mean'),
        avg_views=('views', 'mean'),
        post_count=('post_id', 'count')
    ).reset_index()
    
    grouped['avg_engagement_rate'] = grouped['avg_engagement_rate'].round(2)
    grouped['avg_views'] = grouped['avg_views'].round(0).astype(int)
    
    # Filter combinations with at least 1 post
    top_slots = grouped.sort_values(by='avg_engagement_rate', ascending=False).head(top_n)
    
    results = []
    for _, row in top_slots.iterrows():
        results.append({
            "day": row['day_of_week'],
            "hour": f"{int(row['posting_hour']):02d}:00",
            "slot": row['posting_slot'],
            "avg_engagement_rate": float(row['avg_engagement_rate']),
            "avg_views": int(row['avg_views']),
            "sample_posts": int(row['post_count'])
        })
    return results

def analyze_format_performance(df):
    """
    Aggregates performance by platform and content format.
    """
    fmt_df = df.groupby(['platform', 'format_type']).agg(
        post_count=('post_id', 'count'),
        avg_views=('views', 'mean'),
        avg_likes=('likes', 'mean'),
        avg_comments=('comments', 'mean'),
        avg_shares=('shares', 'mean'),
        avg_engagement_rate=('engagement_rate', 'mean')
    ).reset_index()
    
    fmt_df = fmt_df.round(2)
    return fmt_df.to_dict(orient='records')

def analyze_category_performance(df):
    """
    Aggregates performance across content categories.
    """
    cat_df = df.groupby('category').agg(
        post_count=('post_id', 'count'),
        avg_views=('views', 'mean'),
        avg_likes=('likes', 'mean'),
        avg_engagement_rate=('engagement_rate', 'mean')
    ).reset_index().round(2)
    
    return cat_df.to_dict(orient='records')

def run_analytics_suite(df=None):
    """
    Runs complete analytics suite and exports heatmap CSV.
    """
    if df is None:
        if os.path.exists("data/cleaned_engagement_data.csv"):
            df = pd.read_csv("data/cleaned_engagement_data.csv")
        else:
            from src.etl_pipeline import run_etl
            df = run_etl()
            
    kpis = calculate_kpis(df)
    heatmap_df = generate_posting_heatmap(df)
    top_slots = get_best_posting_slots(df, top_n=5)
    formats = analyze_format_performance(df)
    categories = analyze_category_performance(df)
    
    # Save optimal posting times
    os.makedirs("data", exist_ok=True)
    heatmap_df.to_csv("data/optimal_posting_times.csv")
    print(f"[Analytics] Heatmap analytics saved to 'data/optimal_posting_times.csv'")
    
    return {
        "kpis": kpis,
        "heatmap": heatmap_df.to_dict(),
        "top_slots": top_slots,
        "formats": formats,
        "categories": categories
    }

if __name__ == "__main__":
    results = run_analytics_suite()
    print("KPIs Summary:")
    print(results['kpis'])
    print("\nTop 3 Posting Slots:")
    for slot in results['top_slots'][:3]:
        print(f" -> {slot['day']} at {slot['hour']} ({slot['slot']}) - ER: {slot['avg_engagement_rate']}%")
