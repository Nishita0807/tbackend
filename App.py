from flask import Flask, request, jsonify, send_from_directory
import os
import json
import argparse
from flask_cors import CORS
app = Flask(__name__)
CORS(app) # Enable CORS for your app


app.config["UPLOAD_FOLDER"] = "uploads"
app.config["SUBTITLES_FILE"] = "subtitles.json"

def load_subtitles():
    if os.path.exists(app.config["SUBTITLES_FILE"]):
        with open(app.config["SUBTITLES_FILE"], "r") as f:
            return json.load(f)
    else:
        return {}

def save_subtitles(subtitles):
    with open(app.config["SUBTITLES_FILE"], "w") as f:
        json.dump(subtitles, f)

@app.route("/add_subtitle", methods=["POST"])
def add_subtitle():
    data = request.get_json()
    videoSrc = data.get("videoSrc")
    timestamp = data.get("timestamp")
    subtitle_text = data.get("subtitle_text")

    all_subtitles = load_subtitles()

    if videoSrc not in all_subtitles:
        all_subtitles[videoSrc] = []

    all_subtitles[videoSrc].append({
        "timestamp": timestamp,
        "text": subtitle_text
    })

    save_subtitles(all_subtitles)

    return jsonify({"message": "Subtitle added successfully"}), 200

@app.route("/upload", methods=["POST"])
def upload_video():
    if "video" not in request.files:
        return jsonify({"message": "No video part"}), 400

    video = request.files["video"]
    if video.filename == "":
        return jsonify({"message": "No selected file"}), 400

    video.save(os.path.join(app.config["UPLOAD_FOLDER"], video.filename))
    return jsonify({"message": "Video uploaded successfully"}), 200

@app.route("/get_subtitles/<video_filename>")
def get_subtitles(video_filename):
    all_subtitles = load_subtitles()
    if video_filename in all_subtitles:
        return jsonify({"subtitles": all_subtitles[video_filename]})
    else:
        return jsonify({"subtitles": []})

@app.route("/uploads/<filename>")
def serve_video(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5000, help="Port number to run the server on")
    args = parser.parse_args()
    
    app.run(host="0.0.0.0", port=args.port)
    
