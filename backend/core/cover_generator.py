from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import Optional


def create_cover_image(
    title: str,
    author: str,
    output_path: Path,
    description: str = "",
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
        desc_font = ImageFont.truetype(
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", 20
        )
    except:
        title_font = ImageFont.load_default()
        author_font = ImageFont.load_default()
        desc_font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = bbox[2] - bbox[0]
    title_x = (width - title_width) // 2
    title_y = height // 4

    draw.text((title_x, title_y), title, fill=text_color, font=title_font)

    bbox = draw.textbbox((0, 0), author, font=author_font)
    author_width = bbox[2] - bbox[0]
    author_x = (width - author_width) // 2
    author_y = title_y + 80

    draw.text((author_x, author_y), author, fill=text_color, font=author_font)

    if description:
        max_width = width - 80
        desc_y = author_y + 60
        words = description.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            bbox = draw.textbbox((0, 0), test_line, font=desc_font)
            if bbox[2] - bbox[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=desc_font)
            line_width = bbox[2] - bbox[0]
            line_x = (width - line_width) // 2
            draw.text((line_x, desc_y), line, fill=text_color, font=desc_font)
            desc_y += 30

    img.save(output_path)
    return output_path


def create_cover_with_image(
    image_path: Path,
    output_path: Path,
    title: str = "",
    author: str = "",
    description: str = "",
) -> Path:
    img = Image.open(image_path)
    img = img.convert("RGB")
    img.save(output_path)
    return output_path
