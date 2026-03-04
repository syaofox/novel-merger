from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import Optional


def create_cover_image(
    title: str,
    author: str,
    output_path: Path,
    bg_color: str = "#2c3e50",
    text_color: str = "#ecf0f1",
    width: int = 600,
    height: int = 800,
) -> Path:
    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype(
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", 48
        )
        author_font = ImageFont.truetype(
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", 32
        )
    except:
        title_font = ImageFont.load_default()
        author_font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = bbox[2] - bbox[0]
    title_x = (width - title_width) // 2
    title_y = height // 3

    draw.text((title_x, title_y), title, fill=text_color, font=title_font)

    bbox = draw.textbbox((0, 0), author, font=author_font)
    author_width = bbox[2] - bbox[0]
    author_x = (width - author_width) // 2
    author_y = title_y + 80

    draw.text((author_x, author_y), author, fill=text_color, font=author_font)

    img.save(output_path)
    return output_path
