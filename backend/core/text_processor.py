import re
from typing import List, Tuple


CHAPTER_PATTERNS = [
    r"^第[一二三四五六七八九十百千万\d]+章\s*.*$",
    r"^Chapter\s+\d+\s*.*$",
    r"^第[一二三四五六七八九十百千万\d]+卷\s*.*$",
    r"^第[一二三四五六七八九十百千万\d]+部\s*.*$",
]


def detect_chapters(text: str) -> List[Tuple[int, str]]:
    chapters = []
    lines = text.split("\n")

    for i, line in enumerate(lines):
        line = line.strip()
        for pattern in CHAPTER_PATTERNS:
            if re.match(pattern, line):
                chapters.append((i, line))
                break

    return chapters


def convert_to_markdown_headers(text: str) -> str:
    lines = text.split("\n")
    result = []

    in_chapter = False
    for line in lines:
        line_stripped = line.strip()
        is_chapter = False

        for pattern in CHAPTER_PATTERNS:
            if re.match(pattern, line_stripped):
                is_chapter = True
                break

        if is_chapter:
            result.append(f"\n# {line_stripped}\n")
            in_chapter = True
        elif in_chapter and line_stripped:
            result.append(line)
        else:
            result.append(line)

    return "\n".join(result)


def clean_content(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"^[ \t]+$", "", text, flags=re.MULTILINE)

    text = re.sub(r"^---+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\*\*\*+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^___+$", "", text, flags=re.MULTILINE)

    ad_patterns = [
        r"请访问.*?最新章节",
        r"手机用户请访问",
        r"本章未完.*?下一页",
    ]
    for pattern in ad_patterns:
        text = re.sub(pattern, "", text)

    return text.strip()


def split_into_chapters(text: str) -> List[str]:
    chapter_pattern = r"(第[一二三四五六七八九十百千万\d]+章)"
    parts = re.split(chapter_pattern, text)

    chapters = []
    for i in range(1, len(parts), 2):
        chapter_title = parts[i]
        chapter_content = parts[i + 1] if i + 1 < len(parts) else ""
        chapters.append(f"# {chapter_title}\n\n{chapter_content}")

    return chapters if chapters else [text]
