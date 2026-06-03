"""文档解析服务模块

支持解析 PDF、DOCX、TXT、MD 文件，提取纯文本内容。
"""

import os

from pypdf import PdfReader
from docx import Document


ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


def get_file_type(filename: str) -> str | None:
    """从文件名提取类型，不支持的类型返回 None"""
    ext = os.path.splitext(filename)[1].lower()
    if ext in ALLOWED_EXTENSIONS:
        return ext.lstrip(".")
    return None


def parse_document(file_path: str, file_type: str) -> str | None:
    """解析文档内容，返回纯文本。解析失败返回 None"""
    try:
        if file_type == "txt" or file_type == "md":
            return _parse_text(file_path)
        elif file_type == "pdf":
            return _parse_pdf(file_path)
        elif file_type == "docx":
            return _parse_docx(file_path)
    except Exception:
        return None
    return None


def _parse_text(file_path: str) -> str:
    """解析纯文本文件（TXT/MD）"""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def _parse_pdf(file_path: str) -> str:
    """解析 PDF 文件，提取所有页面文本"""
    reader = PdfReader(file_path)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n\n".join(pages)


def _parse_docx(file_path: str) -> str:
    """解析 DOCX 文件，提取所有段落文本"""
    doc = Document(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)
