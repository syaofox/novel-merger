import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from fastapi import FastAPI, UploadFile, File, Form, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from typing import List, Optional
import tempfile
import os
import re
import shutil
from pathlib import Path

from core.file_handler import (
    sort_files_by_name,
    sort_files_by_custom_order,
    save_upload_file,
    read_file_content,
)
from core.text_processor import (
    convert_to_markdown_headers,
    clean_content,
    split_into_chapters,
    sanitize_for_xml,
)
from core.converter import convert_to_epub
from core.cover_generator import create_cover_image, create_cover_with_image


def clean_metadata_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"[\r\n]+", "", text)
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


app = FastAPI(title="小说合并工具")
api_router = APIRouter()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "小说合并工具 API"}


@api_router.post("/merge")
async def merge_novel(
    files: List[UploadFile] = File(...),
    book_title: str = Form("未命名小说"),
    author: str = Form("未知作者"),
    description: str = Form(""),
    order: Optional[str] = Form(None),
    generate_cover: bool = Form(True),
    cover_image: Optional[UploadFile] = None,
):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        book_title = clean_metadata_text(book_title)
        author = clean_metadata_text(author)
        description = clean_metadata_text(description)

        uploaded_files = []

        for upload_file in files:
            file_path = temp_path / upload_file.filename
            content = await upload_file.read()
            file_path.write_bytes(content)
            uploaded_files.append(file_path)

        file_names = [f.name for f in uploaded_files]

        if order:
            order_list = [int(x) for x in order.split(",")]
            sorted_files = sort_files_by_custom_order(uploaded_files, order_list)
        else:
            sorted_files = sort_files_by_name(file_names)
            sorted_files = [temp_path / f for f in sorted_files]

        all_content = []
        for file_path in sorted_files:
            content = read_file_content(file_path)
            content = sanitize_for_xml(content)
            content = clean_content(content)
            content = convert_to_markdown_headers(content)
            all_content.append(content)

        merged_content = "\n\n".join(all_content)

        output_filename = f"{book_title}.epub"
        output_path = temp_path / output_filename

        cover_path = None
        if generate_cover:
            try:
                cover_path = temp_path / "cover.jpg"
                if cover_image:
                    image_content = await cover_image.read()
                    image_path = temp_path / "uploaded_cover.jpg"
                    image_path.write_bytes(image_content)
                    create_cover_with_image(image_path, cover_path)
                else:
                    create_cover_image(book_title, author, cover_path, description)
            except Exception as e:
                logger.error(f"Cover creation failed: {e}")
                cover_path = None

        convert_to_epub(
            markdown_content=merged_content,
            output_path=output_path,
            book_title=book_title,
            author=author,
            cover_path=cover_path,
            description=description,
        )

        from urllib.parse import quote

        file_content = output_path.read_bytes()

        import io

        return StreamingResponse(
            io.BytesIO(file_content),
            media_type="application/epub+zip",
            headers={
                "Content-Disposition": f"attachment; filename={quote(output_filename)}"
            },
        )


@api_router.post("/preview")
async def preview_merge(
    files: List[UploadFile] = File(...), order: Optional[str] = Form(None)
):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        uploaded_files = []

        for upload_file in files:
            file_path = temp_path / upload_file.filename
            content = await upload_file.read()
            file_path.write_bytes(content)
            uploaded_files.append(file_path)

        if order:
            order_list = [int(x) for x in order.split(",")]
            sorted_files = sort_files_by_custom_order(uploaded_files, order_list)
        else:
            sorted_files = sort_files_by_name([f.name for f in uploaded_files])
            sorted_files = [temp_path / f for f in sorted_files]

        all_content = []
        for file_path in sorted_files:
            content = read_file_content(file_path)
            content = sanitize_for_xml(content)
            content = clean_content(content)
            content = convert_to_markdown_headers(content)
            all_content.append(content)

        merged_content = "\n\n".join(all_content)

        return {"content": merged_content[:5000]}


app.include_router(api_router, prefix="/api")
