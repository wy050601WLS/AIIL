"""知识库文档路由模块

提供文档上传、列表、详情、更新和删除功能。
前缀：/knowledge，所有端点需登录。
"""

import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.conversation import KnowledgeDocument
from app.models.user import User
from app.schemas.conversation import DocumentResponse, DocumentListResponse, DocumentUpdate
from app.services.document_parser import get_file_type, parse_document
from app.utils.security import get_current_user

router = APIRouter(prefix="/knowledge", tags=["知识库"])


@router.post("/upload", response_model=DocumentResponse)
def upload_document(
    file: UploadFile = File(...),
    title: str = Form(None),
    tags: str = Form(None),
    visibility: str = Form("public"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """上传文档文件，自动解析内容并存储"""
    # 校验文件类型
    file_type = get_file_type(file.filename or "")
    if not file_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的文件类型，仅支持 PDF、DOCX、TXT、MD",
        )

    # 读取文件内容并校验大小
    content = file.file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制（最大 {settings.MAX_FILE_SIZE // 1024 // 1024}MB）",
        )

    # 生成存储路径：uploads/knowledge/{user_id}/{uuid}.{ext}
    upload_dir = os.path.join(settings.UPLOAD_DIR, "knowledge", str(user.id))
    os.makedirs(upload_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.{file_type}"
    save_path = os.path.join(upload_dir, filename)

    # 保存文件到磁盘
    with open(save_path, "wb") as f:
        f.write(content)

    # 解析文档内容
    content_text = parse_document(save_path, file_type)

    # BUG4: 解析失败时清理文件并返回错误
    if content_text is None:
        os.remove(save_path)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="文档解析失败，可能是扫描版 PDF 或文件已损坏")

    # 标题默认取文件名（去掉扩展名）
    doc_title = title.strip() if title else os.path.splitext(file.filename or "未命名")[0]

    # 存入数据库
    doc = KnowledgeDocument(
        user_id=user.id,
        title=doc_title,
        file_type=file_type,
        file_path=save_path,
        file_size=len(content),
        content_text=content_text,
        tags=tags.strip() if tags else None,
        visibility=visibility if visibility in ("public", "private", "draft") else "public",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("", response_model=list[DocumentListResponse])
def list_documents(
    keyword: str | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取文档列表（公开文档 + 自己的文档），支持关键词搜索标题和标签。不含全文内容。"""
    from sqlalchemy import or_
    query = db.query(KnowledgeDocument).filter(
        or_(KnowledgeDocument.visibility == "public", KnowledgeDocument.user_id == user.id)
    )
    if keyword and keyword.strip():
        # BUG8: 转义 LIKE 通配符，避免 % 和 _ 被当作通配符
        escaped = keyword.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        q = f"%{escaped}%"
        query = query.filter(
            (KnowledgeDocument.title.like(q, escape="\\")) | (KnowledgeDocument.tags.like(q, escape="\\"))
        )
    return query.order_by(KnowledgeDocument.created_at.desc()).limit(200).all()


@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document(doc_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取文档详情（含全文内容），仅公开文档或自己的文档可访问"""
    from sqlalchemy import or_
    doc = db.query(KnowledgeDocument).filter(
        KnowledgeDocument.id == doc_id,
        or_(KnowledgeDocument.visibility == "public", KnowledgeDocument.user_id == user.id),
    ).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")
    return doc


@router.put("/{doc_id}", response_model=DocumentResponse)
def update_document(doc_id: int, data: DocumentUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """更新文档标题和标签"""
    doc = db.query(KnowledgeDocument).filter(
        KnowledgeDocument.id == doc_id,
        KnowledgeDocument.user_id == user.id,
    ).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")
    if data.title is not None:
        doc.title = data.title
    if data.tags is not None:
        doc.tags = data.tags
    if data.visibility is not None:
        doc.visibility = data.visibility
    db.commit()
    db.refresh(doc)
    return doc


@router.delete("/{doc_id}")
def delete_document(doc_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """删除文档（同时删除磁盘文件）"""
    doc = db.query(KnowledgeDocument).filter(
        KnowledgeDocument.id == doc_id,
        KnowledgeDocument.user_id == user.id,
    ).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")

    # 删除磁盘文件
    if doc.file_path and os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    db.delete(doc)
    db.commit()
    return {"message": "文档已删除"}
