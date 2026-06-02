"""对话模板路由模块

提供对话模板的 CRUD 操作：创建、列表查询、更新、删除。
内置模板（user_id=NULL）对所有用户可见，用户自建模板仅自己可见。
前缀：/templates，所有端点需登录。
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.conversation import PromptTemplate
from app.models.user import User
from app.schemas.conversation import TemplateCreate, TemplateUpdate, TemplateResponse
from app.utils.security import get_current_user

router = APIRouter(prefix="/templates", tags=["对话模板"])

# 系统内置模板列表，首次访问时自动写入数据库
BUILTIN_TEMPLATES = [
    {"title": "翻译为中文", "category": "翻译", "content": "请将以下内容翻译为中文，并解释关键术语："},
    {"title": "概念解释", "category": "解释", "content": "请用简单易懂的语言解释以下概念，并举一个实际例子："},
    {"title": "练习题", "category": "练习", "content": "请根据以下知识点，生成 3 道练习题（含答案）："},
    {"title": "代码审查", "category": "编程", "content": "请审查以下代码，指出潜在问题并给出改进建议："},
    {"title": "总结要点", "category": "写作", "content": "请将以下内容总结为 5 个要点，并突出核心观点："},
]


def _ensure_builtin_templates(db: Session) -> None:
    """若数据库中尚无内置模板，则批量插入 BUILTIN_TEMPLATES"""
    exists = db.query(PromptTemplate).filter(PromptTemplate.is_builtin == True).first()
    if not exists:
        for t in BUILTIN_TEMPLATES:
            db.add(PromptTemplate(
                user_id=None,
                title=t["title"],
                content=t["content"],
                category=t["category"],
                is_builtin=True,
            ))
        db.commit()


@router.get("", response_model=list[TemplateResponse])
def list_templates(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取模板列表：内置模板 + 当前用户的自建模板，内置优先"""
    _ensure_builtin_templates(db)
    return (
        db.query(PromptTemplate)
        .filter(
            (PromptTemplate.is_builtin == True) | (PromptTemplate.user_id == user.id)
        )
        .order_by(PromptTemplate.is_builtin.desc(), PromptTemplate.created_at.desc())
        .all()
    )


@router.post("", response_model=TemplateResponse)
def create_template(data: TemplateCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """创建自定义对话模板"""
    tpl = PromptTemplate(
        user_id=user.id,
        title=data.title,
        content=data.content,
        category=data.category,
        is_builtin=False,
    )
    db.add(tpl)
    db.commit()
    db.refresh(tpl)
    return tpl


@router.put("/{template_id}", response_model=TemplateResponse)
def update_template(template_id: int, data: TemplateUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """更新自定义模板（仅更新非空字段，内置模板不可修改）"""
    tpl = db.query(PromptTemplate).filter(
        PromptTemplate.id == template_id,
        PromptTemplate.user_id == user.id,
        PromptTemplate.is_builtin == False,
    ).first()
    if not tpl:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="模板不存在或不可修改")
    if data.title is not None:
        tpl.title = data.title
    if data.content is not None:
        tpl.content = data.content
    if data.category is not None:
        tpl.category = data.category
    db.commit()
    db.refresh(tpl)
    return tpl


@router.delete("/{template_id}")
def delete_template(template_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """删除自定义模板（内置模板不可删除）"""
    tpl = db.query(PromptTemplate).filter(
        PromptTemplate.id == template_id,
        PromptTemplate.user_id == user.id,
        PromptTemplate.is_builtin == False,
    ).first()
    if not tpl:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="模板不存在或不可删除")
    db.delete(tpl)
    db.commit()
    return {"message": "模板已删除"}
