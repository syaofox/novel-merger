import pypandoc
from pathlib import Path
from typing import Optional
import os


def convert_to_epub(
    markdown_content: str,
    output_path: Path,
    book_title: str,
    author: str,
    cover_path: Optional[Path] = None,
    description: str = "",
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    template_path = Path(__file__).parent.parent / "templates" / "epub3.html"

    yaml_metadata = f"""---
title: {book_title}
author: {author}
creator: {author}
"""
    if description:
        yaml_metadata += f"subtitle: {description}\n"
    yaml_metadata += "---\n\n"

    final_content = yaml_metadata + markdown_content

    extra_args = [
        "--standalone",
        f"--template={template_path}",
    ]

    if cover_path and cover_path.exists():
        extra_args.append(f"--epub-cover-image={str(cover_path)}")

    pypandoc.convert_text(
        source=final_content,
        format="md",
        to="epub",
        outputfile=str(output_path),
        extra_args=extra_args,
    )

    output_path.chmod(0o644)

    return output_path


def convert_to_markdown(text: str, input_format: str = "txt") -> str:
    if input_format == "txt":
        return text
    elif input_format == "md":
        return text
    else:
        raise ValueError(f"Unsupported input format: {input_format}")
