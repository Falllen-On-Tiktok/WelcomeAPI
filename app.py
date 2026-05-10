from flask import Flask, request, jsonify
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import os
import time

app = Flask(__name__)

os.makedirs("static", exist_ok=True)

# ---- SAFE FONT LOADER (prevents Render crash) ----
def load_font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except:
        return ImageFont.load_default()

@app.route("/banner", methods=["GET"])
def banner():
    try:
        username = request.args.get("username", "Unknown")
        member = request.args.get("member", "0")
        avatar_url = request.args.get("avatar")
        event_type = request.args.get("type", "join")

        # ---- BACKGROUND SWITCH ----
        if event_type == "leave":
            bg = Image.open("leave.jpg").convert("RGBA")
            status_text = "Has Departed from CVIA!"
        else:
            bg = Image.open("join.jpg").convert("RGBA")
            status_text = "Has Landed at CVIA!"

        width, height = bg.size
        draw = ImageDraw.Draw(bg)

        # ---- YOUR REQUIRED FONT SIZES ----
        font = load_font(125)
        small_font = load_font(120)

        # ---- TEXT POSITION (UPDATED AS REQUESTED) ----
        text_x = 80
        text_y = height // 2 - 200

        draw.text(
            (text_x, text_y),
            f"Flight #MBRS-{member}",
            fill="white",
            font=font
        )

        draw.text(
            (text_x, text_y + 135),
            status_text,
            fill="white",
            font=small_font
        )

        # ---- AVATAR (CENTER CIRCLE, SIZE 440) ----
        if avatar_url:
            response = requests.get(avatar_url)
            avatar = Image.open(BytesIO(response.content)).convert("RGBA")

            size = 440
            avatar = avatar.resize((size, size))

            mask = Image.new("L", (size, size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, size, size), fill=255)

            avatar.putalpha(mask)

            center_x = width // 2
            center_y = height // 2

            bg.paste(
                avatar,
                (center_x - size // 2, center_y - size // 2),
                avatar
            )

        # ---- SAVE FILE ----
        filename = f"{int(time.time() * 1000)}.png"
        filepath = f"static/{filename}"
        bg.save(filepath)

        return jsonify({
            "url": f"https://welcomeapi-3wqc.onrender.com/static/{filename}"
        })

    except Exception as e:
        # This prevents Render full crash spam
        return jsonify({"error": str(e)}), 500


@app.route("/static/<path:filename>")
def static_files(filename):
    return app.send_static_file(filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
