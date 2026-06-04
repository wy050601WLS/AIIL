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
    {
        "title": "翻译为中文",
        "category": "翻译",
        "content": (
            "请将以下内容翻译为中文。要求：\n"
            "1. 保持原文的语气和风格\n"
            "2. 专业术语在括号中附上英文原文\n"
            "3. 如有歧义的翻译，列出备选方案\n\n"
            "待翻译内容：\n"
        ),
    },
    {
        "title": "概念解释",
        "category": "解释",
        "content": (
            "请解释以下概念。要求：\n"
            "1. 先用一句话概括核心含义\n"
            "2. 再用通俗易懂的语言展开说明\n"
            "3. 给出一个贴近生活的实际例子\n"
            "4. 如果有相关概念，用表格对比异同\n\n"
            "待解释概念：\n"
        ),
    },
    {
        "title": "练习题",
        "category": "练习",
        "content": (
            "请根据以下知识点生成练习题。要求：\n"
            "1. 生成 3 道题，难度由浅入深\n"
            "2. 包含选择题和简答题各类型\n"
            "3. 每道题附上详细答案和解题思路\n"
            "4. 标注每道题考查的知识点\n\n"
            "知识点：\n"
        ),
    },
    {
        "title": "代码审查",
        "category": "编程",
        "content": (
            "请审查以下代码。要求：\n"
            "1. 指出潜在的 bug 或逻辑错误\n"
            "2. 分析性能问题和可优化之处\n"
            "3. 检查代码风格和命名规范\n"
            "4. 给出修改后的完整代码\n\n"
            "待审查代码：\n"
        ),
    },
    {
        "title": "总结要点",
        "category": "写作",
        "content": (
            "请总结以下内容的要点。要求：\n"
            "1. 提取 5 个核心要点，按重要性排序\n"
            "2. 每个要点用一句话概括\n"
            "3. 用粗体标注关键词\n"
            "4. 最后给出一句话的全局总结\n\n"
            "待总结内容：\n"
        ),
    },
    {
        "title": "错题分析",
        "category": "学习",
        "content": (
            "我做错了以下题目，请帮我分析。要求：\n"
            "1. 指出错误原因（概念混淆/计算失误/审题不清等）\n"
            "2. 给出正确的解题过程\n"
            "3. 总结同类题目的解题技巧\n"
            "4. 推荐 2 道类似题目巩固练习\n\n"
            "错题内容：\n"
        ),
    },
    {
        "title": "学习计划",
        "category": "学习",
        "content": (
            "请帮我制定学习计划。要求：\n"
            "1. 明确学习目标和预期成果\n"
            "2. 按周拆分学习任务\n"
            "3. 每周列出具体的学习内容和练习\n"
            "4. 标注重点和难点，给出攻克建议\n\n"
            "学习主题和时间安排：\n"
        ),
    },
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
