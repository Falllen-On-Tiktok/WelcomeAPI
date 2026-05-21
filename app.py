from flask import Flask, request, jsonify
from PIL import Image, ImageDraw
import requests
from io import BytesIO
import os
import time

app = Flask(__name__)

os.makedirs("static", exist_ok=True)

@app.route("/banner", methods=["GET"])
def banner():
    try:
        avatar_url = request.args.get("avatar")
        event_type = request.args.get("type", "join")  # join or leave

        # ---- BACKGROUND SWITCH ----
        if event_type == "leave":
            bg = Image.open("leave.jpg").convert("RGBA")
        else:
            bg = Image.open("join.jpg").convert("RGBA")

        width, height = bg.size

        # ---- AVATAR ----
        if avatar_url and avatar_url.startswith("http"):
            response = requests.get(avatar_url, timeout=5)

            if "image" not in response.headers.get("Content-Type", ""):
                raise ValueError("Invalid image URL")

            avatar = Image.open(BytesIO(response.content)).convert("RGBA")

            # REQUIRED SIZE
            size = 440
            avatar = avatar.resize((size, size))

            # CIRCLE MASK
            mask = Image.new("L", (size, size), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size, size), fill=255)

            avatar.putalpha(mask)

            # CENTER POSITION
            x = (width - size) // 2
            y = (height - size) // 2

            bg.paste(avatar, (x, y), avatar)

        # ---- SAVE OUTPUT ----
        filename = f"{int(time.time() * 1000)}.png"
        path = f"static/{filename}"
        bg.save(path)

        return jsonify({
            "url": f"https://welcomeapi-6ujg.onrender.com/static/{filename}"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/static/<path:filename>")
def static_files(filename):
    return app.send_static_file(filename)
@app.route("/ping")
def ping():
    return "awake"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
