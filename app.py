from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

app = Flask(__name__)

@app.route("/banner", methods=["GET"])
def banner():
    username = request.args.get("username", "Unknown")
    member = request.args.get("member", "0")
    avatar_url = request.args.get("avatar")

    bg = Image.open("background.jpg").convert("RGBA")
    draw = ImageDraw.Draw(bg)
    font = ImageFont.truetype("arial.ttf", 50)

    draw.text((100, 100), f"{username} has just landed!", fill="white", font=font)
    draw.text((100, 170), f"Member #{member}", fill="white", font=font)

    if avatar_url:
        response = requests.get(avatar_url)
        avatar = Image.open(BytesIO(response.content)).resize((180, 180))

        mask = Image.new("L", (180, 180), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, 180, 180), fill=255)

        bg.paste(avatar, (100, 260), mask)

    output = BytesIO()
    bg.save(output, format="PNG")
    output.seek(0)

    return send_file(output, mimetype="image/png")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
