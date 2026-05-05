"""
data_handler.py — CSV upload, validation, preprocessing, and saving utilities.
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"csv"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_upload(file, upload_folder: str) -> str:
    """Save the uploaded file and return its path."""
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_name = f"{timestamp}_{filename}"
    filepath = os.path.join(upload_folder, unique_name)
    file.save(filepath)
    return filepath


def load_and_validate(filepath: str) -> tuple[pd.DataFrame, str | None]:
    """
    Load a CSV and run basic validation.
    Returns (dataframe, error_message). error_message is None on success.
    """
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        return None, f"Could not read CSV: {e}"

    if df.empty:
        return None, "The uploaded CSV is empty."

    if len(df) < 5:
        return None, "Dataset must have at least 5 rows."

    return df, None


def get_numeric_columns(df: pd.DataFrame) -> list[str]:
    """Return column names that are numeric."""
    return df.select_dtypes(include=[np.number]).columns.tolist()


def preview_data(df: pd.DataFrame, n: int = 8) -> dict:
    """Return a JSON-serialisable preview dict for the template."""
    return {
        "columns": df.columns.tolist(),
        "rows": df.head(n).fillna("").values.tolist(),
        "total_rows": len(df),
        "total_cols": len(df.columns),
    }


def save_processed(df: pd.DataFrame, processed_folder: str, original_name: str) -> str:
    """Save the labelled dataframe and return its filename."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = os.path.splitext(os.path.basename(original_name))[0]
    filename = f"{base}_anomaly_{timestamp}.csv"
    filepath = os.path.join(processed_folder, filename)
    df.to_csv(filepath, index=False)
    return filename
