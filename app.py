"""
app.py — Main Flask application for Anomaly Detection Dashboard.
Run: python app.py

Large result data is stored as a JSON file on disk (not in the session cookie)
to avoid the 4 KB browser cookie limit.
"""

import os, json, uuid
import numpy as np
import pandas as pd
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session, send_from_directory, jsonify
)
from utils.data_handler import (
    allowed_file, save_upload, load_and_validate,
    get_numeric_columns, preview_data, save_processed
)
from utils.detector import run_detection, ALGORITHMS

# ── App setup ─────────────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR    = os.path.join(BASE_DIR, "data", "uploads")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
CACHE_DIR     = os.path.join(BASE_DIR, "data", "cache")

for d in (UPLOAD_DIR, PROCESSED_DIR, CACHE_DIR):
    os.makedirs(d, exist_ok=True)

app = Flask(__name__)
app.secret_key = "anomaly_detection_secret_2024"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB

# ── Cache helpers (server-side, avoids cookie size limit) ─────────────────────

def _save_cache(data: dict) -> str:
    cache_id = str(uuid.uuid4())
    with open(os.path.join(CACHE_DIR, f"{cache_id}.json"), "w") as f:
        json.dump(data, f)
    return cache_id

def _load_cache(cache_id):
    if not cache_id:
        return None
    path = os.path.join(CACHE_DIR, f"{cache_id}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)

# ── Sample dataset ────────────────────────────────────────────────────────────

def generate_sample_dataset():
    sample_path = os.path.join(BASE_DIR, "data", "sample_anomaly_dataset.csv")
    if not os.path.exists(sample_path):
        np.random.seed(42)
        n = 300
        n_anom = 15
        df = pd.DataFrame({
            "Machine_ID":  [f"M-{str(i).zfill(3)}" for i in range(1, n + n_anom + 1)],
            "Temperature": np.round(np.concatenate([np.random.normal(72,  3,   n), np.random.uniform(100,130,n_anom)]), 2),
            "Pressure":    np.round(np.concatenate([np.random.normal(100, 5,   n), np.random.uniform(160,200,n_anom)]), 2),
            "Vibration":   np.round(np.concatenate([np.random.normal(0.5, 0.1, n), np.random.uniform(1.5, 3.0,n_anom)]), 3),
            "Current":     np.round(np.concatenate([np.random.normal(15,  1,   n), np.random.uniform(30,  50, n_anom)]), 2),
            "Sensor_Type": np.random.choice(["TypeA","TypeB","TypeC"], n + n_anom),
        }).sample(frac=1, random_state=42).reset_index(drop=True)
        df.to_csv(sample_path, index=False)
    return sample_path

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["GET","POST"])
def upload():
    if request.method == "POST":
        if "file" not in request.files or request.files["file"].filename == "":
            flash("No file selected.", "danger")
            return redirect(request.url)

        file = request.files["file"]
        if not allowed_file(file.filename):
            flash("Only CSV files are allowed.", "danger")
            return redirect(request.url)

        filepath = save_upload(file, UPLOAD_DIR)
        df, error = load_and_validate(filepath)
        if error:
            os.remove(filepath)
            flash(error, "danger")
            return redirect(request.url)

        numeric_cols = get_numeric_columns(df)
        if not numeric_cols:
            os.remove(filepath)
            flash("No numeric columns found in the uploaded CSV.", "danger")
            return redirect(request.url)

        session["filepath"]     = filepath
        session["numeric_cols"] = numeric_cols
        session["preview"]      = preview_data(df)
        session.pop("cache_id", None)

        flash("Dataset uploaded! Configure and run detection below.", "success")
        return redirect(url_for("dashboard"))

    generate_sample_dataset()
    return render_template("upload.html")


@app.route("/sample-download")
def sample_download():
    generate_sample_dataset()
    return send_from_directory(os.path.join(BASE_DIR,"data"),
                               "sample_anomaly_dataset.csv", as_attachment=True)


@app.route("/dashboard", methods=["GET","POST"])
def dashboard():
    if "filepath" not in session:
        flash("Please upload a dataset first.", "warning")
        return redirect(url_for("upload"))

    preview      = session.get("preview", {})
    numeric_cols = session.get("numeric_cols", [])

    if request.method == "POST":
        selected = request.form.getlist("columns")
        algorithm = request.form.get("algorithm", "isolation_forest")
        try:
            contamination = float(request.form.get("contamination", "0.05"))
            contamination = max(0.01, min(0.5, contamination))
        except ValueError:
            contamination = 0.05

        if not selected:
            flash("Please select at least one column.", "danger")
            return render_template("dashboard.html", preview=preview,
                                   numeric_cols=numeric_cols, algorithms=ALGORITHMS)

        df, error = load_and_validate(session["filepath"])
        if error:
            flash(error, "danger")
            return redirect(url_for("upload"))

        result      = run_detection(df, selected, algorithm, contamination)
        df_result   = result["df_result"]
        output_file = save_processed(df_result, PROCESSED_DIR, session["filepath"])

        cache_id = _save_cache({
            "summary":        result["summary"],
            "chart_data":     result["chart_data"],
            "output_file":    output_file,
            "result_table":   df_result.head(200).fillna("").to_dict(orient="records"),
            "result_columns": df_result.columns.tolist(),
        })
        session["cache_id"] = cache_id
        return redirect(url_for("results"))

    return render_template("dashboard.html", preview=preview,
                           numeric_cols=numeric_cols, algorithms=ALGORITHMS)


@app.route("/results")
def results():
    cache = _load_cache(session.get("cache_id"))
    if not cache:
        flash("No results found. Run detection first.", "warning")
        return redirect(url_for("dashboard"))
    return render_template("results.html",
        summary=cache["summary"],
        result_table=cache["result_table"],
        result_columns=cache["result_columns"],
        output_file=cache["output_file"],
        chart_data_json=json.dumps(cache["chart_data"]),
    )


@app.route("/analytics")
def analytics():
    cache = _load_cache(session.get("cache_id"))
    return render_template("analytics.html",
        chart_data_json=json.dumps(cache["chart_data"]) if cache else "{}",
        summary=cache["summary"] if cache else {},
    )


@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(PROCESSED_DIR, filename, as_attachment=True)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/viva")
def viva():
    return render_template("viva.html")


@app.route("/reset")
def reset():
    session.clear()
    flash("Session cleared. Upload a new dataset to start fresh.", "info")
    return redirect(url_for("upload"))


@app.route("/api/chart-data")
def api_chart_data():
    cache = _load_cache(session.get("cache_id"))
    return jsonify(cache["chart_data"] if cache else {})


if __name__ == "__main__":
    generate_sample_dataset()
    print("\n🚀  AnomalyAI is running → http://127.0.0.1:5000\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
