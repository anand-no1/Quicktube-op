from flask import Flask, request, jsonify, send_file
import subprocess
import os
import uuid

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
COOKIES_FILE = "cookies.txt"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


def get_output_path(extension):
    return os.path.join(DOWNLOAD_FOLDER, f"{uuid.uuid4()}.{extension}")


@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get("url")
    format_type = data.get("format", "mp4")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    ext = "mp4" if format_type in ["mp4", "720p", "480p"] else "mp3"
    output_path = get_output_path(ext)

    format_selector = "bestvideo[height<=720]+bestaudio/best[height<=720]" if ext == "mp4" else "bestaudio"
    command = [
        "yt-dlp",
        "-f", format_selector,
        "-o", output_path,
        "--merge-output-format", ext,
        "--no-playlist",
        "--user-agent", "Mozilla/5.0",
        "--geo-bypass",
        "--no-cache-dir"
    ]

    if os.path.exists(COOKIES_FILE):
        command += ["--cookies", COOKIES_FILE]

    command.append(url)

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print("YT-DLP STDOUT:", result.stdout)
        print("YT-DLP STDERR:", result.stderr)
        return send_file(output_path, as_attachment=True)
    except subprocess.CalledProcessError as e:
        print("YT-DLP FAILED:", e.stderr)
        return jsonify({"error": "Download failed", "details": e.stderr}), 500


@app.route('/formats', methods=['POST'])
def list_formats():
    data = request.json
    url = data.get("url")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    command = ["yt-dlp", "--list-formats", url]
    if os.path.exists(COOKIES_FILE):
        command += ["--cookies", COOKIES_FILE]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return jsonify({"formats": result.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Failed to fetch formats", "details": e.stderr}), 500


if __name__ == '__main__':
    app.run(debug=True)