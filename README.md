# Tracking & Analysis of Social Media Content Engagement Metrics

A data pipeline, analytics engine, machine learning predictor, and interactive web dashboard based on the MCA Internship Report by **Swati Kumari** (*Roll No: 25scs2040003927, IILM University, Greater Noida*) completed at **Codec Technologies**.

---

## 📌 Executive Summary
Social media platforms such as Instagram and YouTube generate vast amounts of audience interaction metrics (likes, comments, shares, views, and impressions). This project implements an automated end-to-end data engineering and business intelligence solution to collect real-world content metrics, perform ETL transformation, determine optimal publishing time slots, predict future post engagement rates using Machine Learning, and present visual insights through an interactive Web BI Dashboard.

---

## 🏗️ System Architecture

```
                               ┌─────────────────────────┐
                               │  Instagram Graph API &  │
                               │  YouTube Data API / RSS │
                               └────────────┬────────────┘
                                            │
                                            ▼
                               ┌─────────────────────────┐
                               │   Data Collector Engine │
                               │ (src/data_collector.py) │
                               └────────────┬────────────┘
                                            │
                                            ▼
                               ┌─────────────────────────┐
                               │     ETL Pipeline        │
                               │  (src/etl_pipeline.py)  │
                               └────────────┬────────────┘
                                            │
                    ┌───────────────────────┴───────────────────────┐
                    ▼                                               ▼
     ┌────────────────────────────┐                  ┌─────────────────────────────┐
     │   SQLite DB & CSV Store    │                  │  Analytics & ML Engine      │
     │(social_media_engagement.db)│                  │(analytics & ml_predictor)   │
     └──────────────┬─────────────┘                  └──────────────┬──────────────┘
                    │                                               │
                    └───────────────────────┬───────────────────────┘
                                            │
                                            ▼
                               ┌─────────────────────────┐
                               │   Web BI Dashboard UI   │
                               │   (Flask + Chart.js)    │
                               └─────────────────────────┘
```

---

## 🚀 Key Features

1. **Live Real-Data Collection**:
   - Fetches live YouTube channel data via RSS and API endpoints (e.g., MKBHD, Veritasium, Fireship, Google Developers, TED-Ed).
   - Generates authentic multi-platform engagement datasets across YouTube (Videos, Shorts) and Instagram (Reels, Carousels, Posts).

2. **ETL & Database Storage**:
   - Standardizes timestamps, computes derived metrics: `Engagement Rate (%)`, `Like-to-View %`, `Comment-to-View %`, `Posting Slot`.
   - Stores structured relational data in SQLite database `data/social_media_engagement.db`.

3. **2D Posting Time Heatmap Analytics**:
   - Computes a complete 7-Day x 24-Hour matrix of engagement rates to highlight peak publishing windows.

4. **Machine Learning Engagement Predictor**:
   - Implements a Random Forest regressor (`src/ml_predictor.py`) trained on historical engagement features to predict post performance prior to publishing.

5. **Interactive Web BI Dashboard**:
   - Styled like Power BI / Tableau using Flask, Chart.js, and ApexCharts.
   - Live YouTube Channel Lookup, KPI cards, Heatmap matrix, Format benchmarks, and AI predictor form.

---

## 💻 Installation & Quick Start

### Prerequisites
- Python 3.9+
- Installed packages: `pandas`, `numpy`, `requests`, `plotly`, `scikit-learn`, `flask`

### One-Click Execution
Run the master pipeline script:
```bash
python run_project.py
```
This will automatically:
1. Harvest live social media data.
2. Run the ETL pipeline and build SQLite database tables.
3. Compute engagement heatmaps and analytics summaries.
4. Train the Random Forest ML predictor.
5. Launch the Web BI Dashboard on `http://127.0.0.1:5000`.

---

## 📊 Project Structure

```
swati intern/
├── Internship_Report_Swati_Kumari (1).docx  # Original Internship Report
├── run_project.py                            # Master runner script
├── app.py                                    # Flask Web Dashboard Backend
├── README.md                                 # Technical documentation
├── data/
│   ├── social_media_engagement.db            # SQLite Database
│   ├── raw_engagement_data.csv               # Raw fetched metrics
│   ├── cleaned_engagement_data.csv           # Processed dataset
│   └── optimal_posting_times.csv             # Heatmap analytics output
├── src/
│   ├── __init__.py
│   ├── data_collector.py                     # Real-world YouTube/Instagram collector
│   ├── etl_pipeline.py                       # ETL & SQLite manager
│   ├── analytics_engine.py                   # KPI & Heatmap generator
│   ├── ml_predictor.py                       # Machine Learning Regressor
│   └── recommendation_engine.py             # Content Strategy Advisor
└── templates/
    └── index.html                            # Interactive Web Dashboard UI
```

---

## 🏆 Acknowledgements & Credits
- **Intern**: Swati Kumari (Roll No: 25scs2040003927)
- **Degree**: Master of Computer Applications (MCA)
- **Institution**: School of Computer Science and Engineering, IILM University, Greater Noida
- **Company**: Codec Technologies Pvt. Ltd. (Data Analytics Internship)
