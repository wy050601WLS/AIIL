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
    # ===== 翻译 =====
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
        "title": "翻译为英文",
        "category": "翻译",
        "content": (
            "请将以下内容翻译为英文。要求：\n"
            "1. 使用地道的英文表达，避免中式英语\n"
            "2. 标注重点词汇和短语的用法\n"
            "3. 如有多种表达方式，列出并对比语气差异\n\n"
            "待翻译内容：\n"
        ),
    },
    # ===== 解释 =====
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
        "title": "类比说明",
        "category": "解释",
        "content": (
            "请用类比的方式解释以下概念。要求：\n"
            "1. 找到一个日常生活中的事物作为类比\n"
            "2. 逐步对应类比物和原概念的各个部分\n"
            "3. 指出类比的局限性（哪些方面不完全对应）\n"
            "4. 最后用一句话重新总结概念本身\n\n"
            "待解释概念：\n"
        ),
    },
    {
        "title": "对比分析",
        "category": "解释",
        "content": (
            "请对比分析以下两个概念/技术/方法。要求：\n"
            "1. 用表格列出核心区别（维度：定义/原理/优缺点/适用场景）\n"
            "2. 各给出一个典型使用场景\n"
            "3. 总结选择建议：什么情况下用 A，什么情况下用 B\n\n"
            "待对比的内容：\n"
        ),
    },
    # ===== 练习 =====
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
        "title": "模拟考试",
        "category": "练习",
        "content": (
            "请根据以下内容生成一套模拟考试题。要求：\n"
            "1. 题型包含：选择题 5 道、填空题 3 道、简答题 2 道\n"
            "2. 覆盖所有知识点，难度分布为：基础 40%、中等 40%、提高 20%\n"
            "3. 附上标准答案和评分标准\n"
            "4. 最后给出各知识点的考查频率分析\n\n"
            "考试范围：\n"
        ),
    },
    {
        "title": "记忆口诀",
        "category": "练习",
        "content": (
            "请为以下知识点编写记忆口诀或助记方法。要求：\n"
            "1. 编写朗朗上口的口诀（顺口溜/首字母缩写/谐音等）\n"
            "2. 口诀要准确对应知识点，不能为了押韵牺牲正确性\n"
            "3. 每个口诀附上详细解释，说明每句对应什么\n"
            "4. 如果有常见的记忆误区，一并指出\n\n"
            "知识点：\n"
        ),
    },
    # ===== 编程 =====
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
        "title": "代码解释",
        "category": "编程",
        "content": (
            "请逐行解释以下代码。要求：\n"
            "1. 先给出整体功能概述（一句话）\n"
            "2. 逐行或逐块解释代码逻辑\n"
            "3. 标注关键语法和设计模式\n"
            "4. 指出可以学习的编程技巧\n\n"
            "待解释代码：\n"
        ),
    },
    {
        "title": "Bug 调试",
        "category": "编程",
        "content": (
            "以下代码运行出错，请帮我调试。要求：\n"
            "1. 分析错误信息，定位问题所在\n"
            "2. 解释为什么会出错（根本原因）\n"
            "3. 给出修复方案和修改后的代码\n"
            "4. 总结避免同类错误的方法\n\n"
            "错误信息和代码：\n"
        ),
    },
    {
        "title": "算法分析",
        "category": "编程",
        "content": (
            "请分析以下算法/代码的复杂度。要求：\n"
            "1. 分析时间复杂度（最好/平均/最坏情况）\n"
            "2. 分析空间复杂度\n"
            "3. 用大 O 表示法标注，并解释推导过程\n"
            "4. 如有更优方案，给出并对比\n\n"
            "待分析的算法/代码：\n"
        ),
    },
    # ===== 写作 =====
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
        "title": "作文批改",
        "category": "写作",
        "content": (
            "请批改以下作文/文章。要求：\n"
            "1. 总体评价（立意/结构/语言/创新性，各打 1-5 分）\n"
            "2. 逐段指出优点和可改进之处\n"
            "3. 标注语法错误和用词不当的地方\n"
            "4. 给出 3 条具体的提升建议\n\n"
            "待批改内容：\n"
        ),
    },
    {
        "title": "论文大纲",
        "category": "写作",
        "content": (
            "请为以下主题生成论文/报告大纲。要求：\n"
            "1. 包含引言、正文（3-5 个章节）、结论\n"
            "2. 每个章节列出 2-3 个子要点\n"
            "3. 标注各部分建议的篇幅比例\n"
            "4. 推荐 3-5 个可参考的方向或文献类型\n\n"
            "论文主题：\n"
        ),
    },
    {
        "title": "读书笔记",
        "category": "写作",
        "content": (
            "请帮我整理以下内容的读书笔记。要求：\n"
            "1. 提取核心观点（3-5 个）\n"
            "2. 每个观点附上原文关键句或例子\n"
            "3. 写下自己的思考和联想\n"
            "4. 总结「这本书/这篇文章教会了我什么」\n\n"
            "内容：\n"
        ),
    },
    # ===== 学习 =====
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
    {
        "title": "知识图谱",
        "category": "学习",
        "content": (
            "请为以下主题构建知识图谱。要求：\n"
            "1. 列出核心概念和它们之间的关系\n"
            "2. 用树形或层级结构展示\n"
            "3. 标注每个概念的重要程度（必学/建议了解/拓展）\n"
            "4. 推荐学习顺序（从基础到进阶）\n\n"
            "主题：\n"
        ),
    },
    {
        "title": "考前复习",
        "category": "学习",
        "content": (
            "我即将考试，请帮我快速复习以下内容。要求：\n"
            "1. 提取最高频考点（标注考频）\n"
            "2. 每个考点用最精炼的语言概括\n"
            "3. 列出常见的出题方式和陷阱\n"
            "4. 给出一个 30 分钟的复习路线图\n\n"
            "考试科目和范围：\n"
        ),
    },
    {
        "title": "费曼学习法",
        "category": "学习",
        "content": (
            "请用费曼学习法帮我理解以下内容。要求：\n"
            "1. 假设我是一个 12 岁的学生，用最简单的语言解释这个概念\n"
            "2. 不使用任何专业术语（如必须使用，先解释术语）\n"
            "3. 用一个日常生活的例子来说明\n"
            "4. 最后列出我可能还不理解的难点，逐一解答\n\n"
            "待学习内容：\n"
        ),
    },
    # ===== 数学 =====
    {
        "title": "解题步骤",
        "category": "数学",
        "content": (
            "请详细解答以下数学题。要求：\n"
            "1. 先分析题目，列出已知条件和求解目标\n"
            "2. 说明选择的解题方法和原因\n"
            "3. 分步骤写出解题过程，每步都标注依据\n"
            "4. 验证答案的正确性\n\n"
            "题目：\n"
        ),
    },
    {
        "title": "公式推导",
        "category": "数学",
        "content": (
            "请推导以下公式。要求：\n"
            "1. 从基本定义或已知公式出发\n"
            "2. 每一步推导都标注依据和理由\n"
            "3. 标注关键的推导技巧\n"
            "4. 给出公式的适用条件和常见变形\n\n"
            "待推导的公式：\n"
        ),
    },
    # ===== 英语 =====
    {
        "title": "语法纠错",
        "category": "英语",
        "content": (
            "请检查以下英文的语法错误。要求：\n"
            "1. 逐句检查，标注错误位置\n"
            "2. 说明错误类型（时态/主谓一致/冠词/介词等）\n"
            "3. 给出修改后的句子\n"
            "4. 总结涉及的语法规则\n\n"
            "待检查内容：\n"
        ),
    },
    {
        "title": "句型仿写",
        "category": "英语",
        "content": (
            "请根据以下句型进行仿写练习。要求：\n"
            "1. 分析原句的句型结构\n"
            "2. 给出 5 个仿写例句，覆盖不同场景\n"
            "3. 标注每句中可替换的部分\n"
            "4. 补充 3 个常见变体句型\n\n"
            "原句：\n"
        ),
    },
    {
        "title": "词汇辨析",
        "category": "英语",
        "content": (
            "请辨析以下易混词汇。要求：\n"
            "1. 列出每个词的核心含义和词性\n"
            "2. 用表格对比用法差异\n"
            "3. 每个词给出 2 个典型例句\n"
            "4. 总结记忆区分的技巧\n\n"
            "待辨析词汇：\n"
        ),
    },
]


def _ensure_builtin_templates(db: Session) -> None:
    """确保所有内置模板都存在于数据库中，缺失的自动补全"""
    existing_titles = {
        t.title for t in
        db.query(PromptTemplate.title).filter(PromptTemplate.is_builtin == True).all()
    }
    added = False
    for t in BUILTIN_TEMPLATES:
        if t["title"] not in existing_titles:
            db.add(PromptTemplate(
                user_id=None,
                title=t["title"],
                content=t["content"],
                category=t["category"],
                is_builtin=True,
            ))
            added = True
    if added:
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
