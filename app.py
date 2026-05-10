from flask import Flask, request, jsonify
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import os
import time

app = Flask(__name__)

# Make sure static folder exists
os.makedirs("static", exist_ok=True)

@app.route("/banner", methods=["GET"])
def banner():
    username = request.args.get("username", "Unknown")
    member = request.args.get("member", "0")
    avatar_url = request.args.get("avatar")
    event_type = request.args.get("type", "join")  # join or leave

    # ---- BACKGROUND SWITCH ----
    if event_type == "leave":
        bg = Image.open("leave.jpg").convert("RGBA")
        status_text = "Has Departed from CVIA!"
    else:
        bg = Image.open("join.jpg").convert("RGBA")
        status_text = "Has Landed at CVIA!"

    width, height = bg.size
    draw = ImageDraw.Draw(bg)

    font = ImageFont.truetype("arial.ttf", 125)
    small_font = ImageFont.truetype("arial.ttf", 120)

    # ---- TEXT ----
    text_x = 80
    text_y = height // 2 - 80

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

    # ---- AVATAR (center circle) ----
    if avatar_url:
        response = requests.get(avatar_url)
        avatar = Image.open(BytesIO(response.content)).convert("RGBA")

        size = 220
        avatar = avatar.resize((size, size))

        mask = Image.new("L", (size, size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, size, size), fill=255)

        avatar.putalpha(mask)

        center_x = width // 2
        center_y = height // 2

        bg.paste(avatar, (center_x - size // 2, center_y - size // 2), avatar)

    # ---- SAVE IMAGE ----
    filename = f"{int(time.time() * 1000)}.png"
    filepath = f"static/{filename}"
    bg.save(filepath)

    # ---- RETURN URL ----
    image_url = f"https://welcomeapi-3wqc.onrender.com/static/{filename}"

    return jsonify({
        "url": image_url
    })


# IMPORTANT: serve static files
@app.route("/static/<path:filename>")
def static_files(filename):
    return app.send_static_file(filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
