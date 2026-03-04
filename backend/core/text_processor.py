import re
from typing import List, Tuple


NUM_PATTERN = r"[一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬零〇两\d]"

CHAPTER_MARKER = r"[章回部节集卷]"

CHAPTER_PATTERNS = [
    f"^第{NUM_PATTERN}*{CHAPTER_MARKER}\\s*.*$",
    f"^第{NUM_PATTERN}+卷\\s*.*$",
    f"^第{NUM_PATTERN}+部\\s*.*$",
    r"^Chapter\s+\d+\s*.*$",
    r"^Section\s+\d+\s*.*$",
]


def detect_chapters(text: str) -> List[Tuple[int, str]]:
    chapters = []
    lines = text.split("\n")

    special_keywords = [
        "楔子",
        "尾声",
        "序章",
        "番外",
        "外传",
        "后记",
        "前言",
        "目录",
        "终章",
        "开端",
        "序幕",
        "结局",
        "附录",
        "楔子",
        "尾聲",
        "序章",
        "番外",
        "外傳",
        "後記",
        "前言",
        "目錄",
        "終章",
        "開端",
        "序幕",
        "結局",
        "附錄",
    ]
    special_pattern = "^(" + "|".join(special_keywords) + r")\s*.*$"

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        is_chapter = False
        for pattern in CHAPTER_PATTERNS:
            if re.match(pattern, line):
                is_chapter = True
                break

        if not is_chapter and re.match(special_pattern, line):
            is_chapter = True

        if is_chapter:
            chapters.append((i, line))

    return chapters


def convert_to_markdown_headers(text: str) -> str:
    lines = text.split("\n")
    result = []

    special_keywords = [
        "楔子",
        "尾声",
        "序章",
        "番外",
        "外传",
        "后记",
        "前言",
        "目录",
        "终章",
        "开端",
        "序幕",
        "结局",
        "附录",
        "楔子",
        "尾聲",
        "序章",
        "番外",
        "外傳",
        "後記",
        "前言",
        "目錄",
        "終章",
        "開端",
        "序幕",
        "結局",
        "附錄",
    ]
    special_pattern = "^(" + "|".join(special_keywords) + r")\s*.*$"

    in_chapter = False
    for line in lines:
        line_stripped = line.strip()
        is_chapter = False

        for pattern in CHAPTER_PATTERNS:
            if re.match(pattern, line_stripped):
                is_chapter = True
                break

        if not is_chapter and re.match(special_pattern, line_stripped):
            is_chapter = True

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
        r"請訪問.*?最新章節",
        r"手機用戶請訪問",
        r"本章未完.*?下一頁",
    ]
    for pattern in ad_patterns:
        text = re.sub(pattern, "", text)

    return text.strip()


def split_into_chapters(text: str) -> List[str]:
    chapters_data = detect_chapters(text)

    if not chapters_data:
        return [text]

    lines = text.split("\n")
    chapters = []

    for i, (chapter_line_idx, chapter_title) in enumerate(chapters_data):
        start_pos = sum(len(lines[j]) + 1 for j in range(chapter_line_idx))

        if i + 1 < len(chapters_data):
            next_chapter_line_idx = chapters_data[i + 1][0]
            end_pos = sum(len(lines[j]) + 1 for j in range(next_chapter_line_idx))
        else:
            end_pos = len(text)

        chapter_content = text[start_pos:end_pos].strip()
        chapters.append(f"# {chapter_title}\n\n{chapter_content}")

    return chapters


def sanitize_for_xml(text: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = re.sub(r"<think[^>]*>", "", text, flags=re.IGNORECASE)

    text = re.sub(r"^## \S+ [Uu]ser\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^## \r?\n?$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^## \S+ [Aa]ssistant\s*$", "", text, flags=re.MULTILINE)

    def escape_angle_brackets(s: str) -> str:
        result = []
        i = 0
        while i < len(s):
            if s[i] == "<":
                j = i + 1
                while j < len(s) and s[j] not in (">", " ", "\n", "\t"):
                    j += 1
                tag = s[i : j + 1] if j < len(s) and s[j] == ">" else s[i:j]
                if re.match(r"^[a-zA-Z][a-zA-Z0-9]*>$", tag):
                    result.append(tag)
                    i = j + 1
                else:
                    result.append("&lt;")
                    i += 1
            elif s[i] == ">":
                result.append("&gt;")
                i += 1
            else:
                result.append(s[i])
                i += 1
        return "".join(result)

    text = escape_angle_brackets(text)

    text = re.sub(r"&(?!amp;|lt;|gt;|quot;|apos;|#)", "&amp;", text)

    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    text = text.replace("\ufeff", "")

    return text.strip()
