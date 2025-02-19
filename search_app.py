import os
import re
import json
import shutil

from flask import Flask, request, render_template, send_from_directory, jsonify
import pandas as pd

app = Flask(__name__)
top_n = 10

# Dataset paths
DATASET_ROOT = "/home/alee00/datasets/trellis/ObjaverseXL_sketchfab"
METADATA_FILE = f"{DATASET_ROOT}/metadata.csv"
DOWNLOADED_FILE = f"{DATASET_ROOT}/downloaded_0.csv"
OUTPUT_DIR = "./output"

# Load metadata and downloaded file paths
metadata_df = pd.read_csv(METADATA_FILE)
downloaded_df = pd.read_csv(DOWNLOADED_FILE)

# Merge metadata with downloaded paths using sha256
if "sha256" in metadata_df.columns and "sha256" in downloaded_df.columns:
    metadata_df = metadata_df.merge(downloaded_df[["sha256", "local_path"]], on="sha256", how="left")

keyword_models = {}

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/search", methods=["GET"])
def search():
    keyword = request.args.get("keyword", "").lower()

    if not keyword:
        return "Enter a search query.", 400

    models = keyword_models.get(keyword, None)

    if models is None:
        pattern = rf"\b{re.escape(keyword)}\b"

        # Filter metadata based on keyword in captions
        results = metadata_df[
            metadata_df["captions"].str.lower().str.contains(pattern, na=False, regex=True)
        ]

        if results.empty:
            return render_template("results.html", asset_paths=[])

        models = [
            {
                "path": f"/serve_model/{row['local_path']}", 
                "caption": row["captions"],
                "sha256": row["sha256"]
            }
            for _, row in results.iterrows() if pd.notna(row["local_path"])
        ]

        keyword_models[keyword] = models

    return render_template("results.html", models=models[:top_n], keyword=keyword, total=len(models))

@app.route("/serve_model/<path:filepath>")
def serve_model(filepath):
    """Serve .glb files dynamically from the correct subdirectories."""
    return send_from_directory(DATASET_ROOT, filepath)

@app.route("/load_more", methods=["GET"])
def load_more():
    """Loads more models dynamically for infinite scrolling."""
    keyword = request.args.get("keyword", "").lower()
    offset = int(request.args.get("offset", 0))

    models = keyword_models[keyword]

    more_models = models[offset:offset + top_n]

    return jsonify(more_models)

@app.route("/save_models", methods=["POST"])
def save_models():
    data = request.json
    keyword = data.get("keyword", "").strip()
    selected_models = data.get("models", None)

    if not selected_models:
        return jsonify({"message": "No models selected!"}), 400

    keyword_path = os.path.join(OUTPUT_DIR, keyword)
    os.makedirs(keyword_path, exist_ok=True)

    existing_batches = [
        int(folder) for folder in os.listdir(keyword_path) if folder.isdigit()
    ]
    next_batch = max(existing_batches, default=0) + 1 

    save_path = os.path.join(keyword_path, str(next_batch))
    os.makedirs(save_path, exist_ok=True)

    metadata = []

    for model in selected_models:
        source_path = os.path.join(DATASET_ROOT, model["path"].replace("/serve_model/", "").lstrip("/"))
        filename = os.path.basename(model["path"])
        dest_path = os.path.join(save_path, filename)

        try:
            shutil.copy2(source_path, dest_path)
            metadata.append({
                "path": dest_path,
                "filename": filename,
                "caption": model["caption"],
                "sha256": model["sha256"]
            })
        except Exception as e:
            print(f"Failed to copy {source_path}: {e}")

    metadata_file = os.path.join(save_path, "metadata.json")
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=4)

    return jsonify({"message": f"Saved {len(selected_models)} models to {save_path}!"})

if __name__ == "__main__":
    app.run(debug=True)
