from pathlib import Path
from typing import Optional
import os
import subprocess
import tempfile
import zipfile
import shutil


def convert_to_epub(
    markdown_content: str,
    output_path: Path,
    book_title: str,
    author: str,
    cover_path: Optional[Path] = None,
    description: str = "",
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    metadata_file = None
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yml", delete=False, encoding="utf-8"
    ) as f:
        f.write(f"""---
title: "{book_title}"
author: "{author}"
lang: zh-CN
""")
        if description:
            f.write(f'description: "{description}"\n')
        f.write("---\n")
        metadata_file = f.name

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    ) as f:
        f.write(markdown_content)
        content_file = f.name

    cmd = [
        "pandoc",
        str(content_file),
        "-o",
        str(output_path),
        "--metadata-file",
        metadata_file,
    ]

    if cover_path and cover_path.exists():
        cmd.extend(
            [
                f"--epub-cover-image={str(cover_path)}",
                "--toc",
                "--toc-depth=2",
            ]
        )

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )

    os.unlink(metadata_file)
    os.unlink(content_file)

    if result.returncode != 0:
        raise RuntimeError(f"Pandoc error: {result.stderr}")

    if cover_path and cover_path.exists():
        add_cover_metadata(str(output_path))

    output_path.chmod(0o644)

    return output_path


def add_cover_metadata(epub_path: str) -> None:
    temp_dir = tempfile.mkdtemp()
    try:
        with zipfile.ZipFile(epub_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        content_opf = None
        for root, dirs, files in os.walk(temp_dir):
            for f in files:
                if f == "content.opf":
                    content_opf = os.path.join(root, f)
                    break

        if not content_opf:
            return

        with open(content_opf, "r", encoding="utf-8") as f:
            content = f.read()

        if '<meta name="cover" content="cover_jpg"' in content:
            return

        meta_line = '<meta property="dcterms:modified"'
        insert_line = '    <meta name="cover" content="cover_jpg" />\n'
        content = content.replace(meta_line, insert_line + meta_line)

        with open(content_opf, "w", encoding="utf-8") as f:
            f.write(content)

        with zipfile.ZipFile(epub_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
    finally:
        shutil.rmtree(temp_dir)


def convert_to_markdown(text: str, input_format: str = "txt") -> str:
    if input_format == "txt":
        return text
    elif input_format == "md":
        return text
    else:
        raise ValueError(f"Unsupported input format: {input_format}")
