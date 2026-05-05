# 🔍 AnomalyAI — Anomaly Detection using Machine Learning

> A production-grade Flask web application for detecting anomalies in tabular CSV datasets
> using Isolation Forest, One-Class SVM, and Local Outlier Factor.

---

## 📌 Problem Statement

In large-scale systems such as industrial machinery, financial transactions, and network traffic,
manually identifying abnormal data patterns is impossible at scale. Traditional threshold-based
rules fail to capture complex multi-variate anomalies. This project provides an automated,
ML-driven pipeline that detects anomalies in **any tabular CSV dataset** without requiring
labelled training data (fully unsupervised).

---

## 🎯 Objectives

- Detect anomalies in unlabelled CSV datasets using unsupervised ML
- Support multiple algorithms: Isolation Forest, One-Class SVM, LOF
- Provide interactive visualisations: scatter, line, pie, histogram
- Export labelled output CSV with `Prediction` and `Status` columns
- Include Viva Guide and README for academic/portfolio use

---

## ✨ Features

| Feature | Detail |
|---|---|
| CSV Upload | Drag-and-drop, 16 MB limit, auto column detection |
| Dataset Preview | First 8 rows shown before detection |
| Algorithm Choice | Isolation Forest · One-Class SVM · LOF |
| Contamination Control | Slider from 1% to 50% |
| 4 Chart Types | Scatter · Line · Pie · Histogram |
| Table with Badges | Normal ✅ / Anomaly 🚨 colour-coded |
| CSV Download | Timestamped output with labels |
| Viva Guide | Built-in Q&A for exam/interview preparation |
| Sample Dataset | 315-row industrial sensor data generated on first run |

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11, Flask 3.0, Pandas, NumPy, Scikit-learn
- **Frontend**: HTML5, CSS3 (custom), JavaScript ES6, Chart.js 4
- **ML Models**: IsolationForest, OneClassSVM, LocalOutlierFactor
- **Preprocessing**: StandardScaler (zero mean, unit variance)

---

## 📁 Folder Structure

```
anomaly_detection_flask/
│
├── app.py                    # Flask routes & app entry point
├── requirements.txt
├── README.md
│
├── data/
│   ├── uploads/              # Raw uploaded CSVs (auto-created)
│   ├── processed/            # Labelled output CSVs (auto-created)
│   └── sample_anomaly_dataset.csv  # Auto-generated on first run
│
├── static/
│   ├── css/style.css
│   └── js/dashboard.js
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── upload.html
│   ├── dashboard.html
│   ├── results.html
│   ├── analytics.html
│   ├── about.html
│   └── viva.html
│
└── utils/
    ├── __init__.py
    ├── detector.py           # ML detection logic
    └── data_handler.py       # CSV validation & preprocessing
```

---

## 🚀 How to Run (Windows PowerShell)

### 1. Clone the repository
```powershell
git clone https://github.com/Harsha1704/anomaly_detection_flask.git
cd anomaly_detection_flask
```

### 2. Create a virtual environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

> If you get a script execution error, run first:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### 3. Install dependencies
```powershell
pip install -r requirements.txt
```

### 4. Run the application
```powershell
python app.py
```

### 5. Open in browser
```
http://127.0.0.1:5000
```

---

## 📸 Screenshots

> _(Add screenshots here after running the app)_
>
> - Home page hero
> - Upload page with drag-and-drop
> - Dashboard column selector
> - Results with metric cards and charts
> - Analytics deep-dive view
> - Viva Guide accordion

---

## 📊 Output Format

The downloaded CSV includes all original columns plus:

| Column | Values | Description |
|---|---|---|
| `Anomaly_Score` | float | Model confidence score |
| `Prediction` | 1 or -1 | 1 = Normal, -1 = Anomaly |
| `Status` | Normal / Anomaly | Human-readable label |

---

## 🎓 Viva Explanation (Quick)

> "I built an unsupervised anomaly detection web app using Flask and Scikit-learn. The main
> algorithm is Isolation Forest, which isolates anomalies by randomly partitioning data — anomalies
> need fewer splits to isolate, giving them a shorter path length and lower anomaly score. I used
> StandardScaler for preprocessing, Chart.js for visualisation, and Flask sessions to pass data
> between routes without a database."

---

## 🔮 Future Enhancements

- Deep learning models (Autoencoder, LSTM) for time-series data
- Real-time streaming with WebSockets or Kafka
- User login + detection history with SQLite
- REST API for IoT/Grafana integration
- SHAP-based explainability for individual anomalies
- Docker containerisation for easy deployment

---
## 📄 License

MIT License — free to use for educational and portfolio purposes.
