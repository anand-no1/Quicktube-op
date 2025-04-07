from flask import Flask, request, send_file, jsonify, render_template
import yt_dlp
import os
import uuid

app = Flask(__name__)

DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# Path to cookies.txt (make sure it's inside the same folder as this script or project root)
cookies_path = os.path.join(os.path.dirname(__file__), "cookies.txt")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download_video():
    data = request.get_json()
    url = data.get("url")
    format_type = data.get("format")

    if not url or not format_type:
        return jsonify({"error": "Missing URL or format"}), 400

    temp_id = str(uuid.uuid4())
    output_path = os.path.join(DOWNLOAD_DIR, f"{temp_id}.%(ext)s")

    ydl_opts = {
        "outtmpl": output_path,
        "quiet": True,
        "cookiefile": cookies_path,  # Use cookies to bypass login restrictions
        "noplaylist": True,
        "merge_output_format": "mp3" if format_type == "mp3" else "mp4",
    }

    if format_type.endswith("p"):  # e.g., 720p, 360p
        ydl_opts["format"] = f"bestvideo[height<={format_type[:-1]}]+bestaudio/best"
    else:
        ydl_opts["format"] = "bestaudio/best"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            ext = "mp3" if format_type == "mp3" else "mp4"
            filename = ydl.prepare_filename(info)
            final_file = filename.replace(".webm", f".{ext}").replace(".m4a", f".{ext}")

        return send_file(final_file, as_attachment=True)

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Download failed"}), 500

if __name__ == "__main__":
    app.run(debug=True)