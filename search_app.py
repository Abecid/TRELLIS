from flask import Flask, request, render_template, send_from_directory
import pandas as pd
import os

app = Flask(__name__)
top_n = 10

# Dataset paths
DATASET_ROOT = "/home/alee00/datasets/trellis/ObjaverseXL_sketchfab"
METADATA_FILE = f"{DATASET_ROOT}/metadata.csv"
DOWNLOADED_FILE = f"{DATASET_ROOT}/downloaded_0.csv"

# Load metadata and downloaded file paths
metadata_df = pd.read_csv(METADATA_FILE)
downloaded_df = pd.read_csv(DOWNLOADED_FILE)

# Merge metadata with downloaded paths using sha256
if "sha256" in metadata_df.columns and "sha256" in downloaded_df.columns:
    metadata_df = metadata_df.merge(downloaded_df[["sha256", "local_path"]], on="sha256", how="left")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/search", methods=["GET"])
def search():
    keyword = request.args.get("keyword", "").lower()

    if not keyword:
        return "Enter a search query.", 400

    # Filter metadata based on keyword in captions
    results = metadata_df[metadata_df["captions"].str.lower().str.contains(keyword, na=False)]

    if results.empty:
        return render_template("results.html", asset_paths=[])

    # Generate full asset paths for rendering
    # asset_paths = [os.path.join(DATASET_ROOT, path) for path in results["local_path"].dropna()][:top_n]

    # return render_template("results.html", asset_paths=asset_paths)

    asset_paths = [f"/serve_model/{path}" for path in results["local_path"].dropna()]

    return render_template("results.html", asset_paths=asset_paths)

@app.route("/serve_model/<path:filepath>")
def serve_model(filepath):
    """Serve .glb files dynamically from the correct subdirectories."""
    return send_from_directory(DATASET_ROOT, filepath)

if __name__ == "__main__":
    app.run(debug=True)
