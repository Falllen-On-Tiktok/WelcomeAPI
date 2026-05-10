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
    width, height = bg.size

    draw = ImageDraw.Draw(bg)

    font = ImageFont.truetype("arial.ttf", 55)
    small_font = ImageFont.truetype("arial.ttf", 45)

    # ---- TEXT (center-left vertically aligned) ----
    text_x = 80
    text_y = height // 2 - 80

    draw.text(
        (text_x, text_y),
        f"Flight #MBRS-{member}",
        fill="white",
        font=font
    )

    draw.text(
        (text_x, text_y + 70),
        "Has Landed at CVIA!",
        fill="white",
        font=small_font
    )

    # ---- AVATAR (centered circle) ----
    if avatar_url:
        response = requests.get(avatar_url)
        avatar = Image.open(BytesIO(response.content)).convert("RGBA")

        size = 220
        avatar = avatar.resize((size, size))

        # Create circular mask
        mask = Image.new("L", (size, size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, size, size), fill=255)

        avatar.putalpha(mask)

        # Center of image
        center_x = width // 2
        center_y = height // 2

        bg.paste(
            avatar,
            (center_x - size // 2, center_y - size // 2),
            avatar
        )

    # ---- OUTPUT ----
    output = BytesIO()
    bg.save(output, format="PNG")
    output.seek(0)

    return send_file(output, mimetype="image/png")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
