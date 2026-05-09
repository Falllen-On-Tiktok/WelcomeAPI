from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
import io
import requests

app = Flask(__name__)

@app.route("/card")
def card():
    username = request.args.get("user", "Unknown")
    member = request.args.get("member", "0")
    avatar_url = request.args.get("avatar")

    # Load background
    image = Image.open("background.jpg").convert("RGBA")
    draw = ImageDraw.Draw(image)

    width, height = image.size

    # EVEN BIGGER font
    font = ImageFont.truetype("fonts/arial.ttf", 110)

    line1 = f"{username} has just landed!"
    line2 = f"Member #{member}"

    # Measure text sizes
    def text_size(text):
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    l1_w, l1_h = text_size(line1)
    l2_w, l2_h = text_size(line2)

    avatar_size = 300  # bigger avatar

    total_height = l1_h + 20 + l2_h + 40 + avatar_size

    start_y = (height - total_height) // 2

    # Center text helper
    def draw_center(text, y):
        w, _ = text_size(text)
        x = (width - w) // 2
        draw.text((x, y), text, font=font, fill="white")

    # Draw text (centered block)
    y = start_y
    draw_center(line1, y)
    y += l1_h + 20

    draw_center(line2, y)
    y += l2_h + 40

    # ---------------- CIRCULAR AVATAR ----------------
    if avatar_url:
        try:
            response = requests.get(avatar_url)
            avatar = Image.open(io.BytesIO(response.content)).convert("RGBA")

            avatar = avatar.resize((avatar_size, avatar_size))

            mask = Image.new("L", (avatar_size, avatar_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, avatar_size, avatar_size), fill=255)

            avatar.putalpha(mask)

            x = (width - avatar_size) // 2
            image.paste(avatar, (x, y), avatar)

        except Exception as e:
            print("Avatar load failed:", e)

    # Save to memory
    img_io = io.BytesIO()
    image.save(img_io, "PNG")
    img_io.seek(0)

    return send_file(img_io, mimetype="image/png")


app.run(host="0.0.0.0", port=5000)
