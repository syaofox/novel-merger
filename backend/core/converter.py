import pypandoc
from pathlib import Path
from typing import Optional


def convert_to_epub(
    markdown_content: str,
    output_path: Path,
    book_title: str,
    author: str,
    cover_path: Optional[Path] = None,
) -> Path:
    extra_args = [
        "--standalone",
        f"--metadata=title:{book_title}",
        f"--metadata=creator:{author}",
    ]

    if cover_path and cover_path.exists():
        extra_args.append(f"--epub-cover-image={str(cover_path)}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    pypandoc.convert_text(
        source=markdown_content,
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
