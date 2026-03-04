import re
from typing import List, Tuple
from pathlib import Path


def sort_files_by_name(files: List[str]) -> List[str]:
    def extract_number(filename: str) -> tuple:
        match = re.match(r"^(\d+)", Path(filename).stem)
        if match:
            return (0, int(match.group(1)), filename)
        return (1, 0, filename)

    return sorted(files, key=extract_number)


def sort_files_by_custom_order(files: List[str], order: List[int]) -> List[str]:
    if len(files) != len(order):
        raise ValueError("Files count does not match order count")

    indexed_files = list(zip(order, files))
    indexed_files.sort(key=lambda x: x[0])
    return [f for _, f in indexed_files]


async def save_upload_file(upload_file, temp_dir: Path) -> Path:
    file_path = temp_dir / upload_file.filename
    content = await upload_file.read()
    file_path.write_bytes(content)
    return file_path


def read_file_content(file_path: Path | str) -> str:
    file_path = Path(file_path)
    encodings = ["utf-8", "gbk", "gb2312", "big5"]

    for encoding in encodings:
        try:
            return file_path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue

    raise ValueError(f"Unable to decode file: {file_path}")
