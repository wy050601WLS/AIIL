"""学习面板路由模块

提供学习统计数据：对话数、消息数、卡片数、活跃天数、每日消息趋势、热门标签。
前缀：/dashboard，需登录。
"""

from collections import Counter
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.conversation import Conversation, KnowledgeCard, Message
from app.models.user import User
from app.schemas.conversation import DashboardStats, DailyMessage, TagCount
from app.utils.security import get_current_user

router = APIRouter(prefix="/dashboard", tags=["学习面板"])


@router.get("/stats", response_model=DashboardStats)
def get_stats(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取学习面板统计数据

    返回：
    - conversation_count: 用户的对话总数
    - message_count: 用户的消息总数（通过 join conversations 关联）
    - card_count: 用户的知识卡片数
    - active_days: 最近 30 天有消息的天数
    - daily_messages: 最近 30 天每天的消息数（用于柱状图）
    - top_tags: 知识卡片标签 Top 10（用于标签分布展示）
    """
    # 对话数
    conversation_count = db.query(func.count(Conversation.id)).filter(
        Conversation.user_id == user.id
    ).scalar()

    # 消息数（通过 join conversations 关联到用户）
    message_count = db.query(func.count(Message.id)).join(Conversation).filter(
        Conversation.user_id == user.id
    ).scalar()

    # 知识卡片数
    card_count = db.query(func.count(KnowledgeCard.id)).filter(
        KnowledgeCard.user_id == user.id
    ).scalar()

    # 最近 30 天每日消息数（GROUP BY 日期）
    since = datetime.now() - timedelta(days=29)
    rows = (
        db.query(func.date(Message.created_at).label("day"), func.count(Message.id))
        .join(Conversation)
        .filter(Conversation.user_id == user.id, Message.created_at >= since)
        .group_by(func.date(Message.created_at))
        .all()
    )
    day_map = {str(r[0]): r[1] for r in rows}
    daily_messages = []
    for i in range(30):
        d = (since + timedelta(days=i)).strftime("%Y-%m-%d")
        daily_messages.append(DailyMessage(date=d, count=day_map.get(d, 0)))

    # 活跃天数：最近 30 天中有消息的天数
    active_days = len([d for d in daily_messages if d.count > 0])

    # 热门标签：拆分所有卡片的 tags 字段，统计出现次数 Top 10
    cards = db.query(KnowledgeCard.tags).filter(
        KnowledgeCard.user_id == user.id, KnowledgeCard.tags.isnot(None)
    ).all()
    tag_counter: Counter = Counter()
    for (tags_str,) in cards:
        for tag in tags_str.split(","):
            tag = tag.strip()
            if tag:
                tag_counter[tag] += 1
    top_tags = [TagCount(tag=t, count=c) for t, c in tag_counter.most_common(10)]

    return DashboardStats(
        conversation_count=conversation_count,
        message_count=message_count,
        card_count=card_count,
        active_days=active_days,
        daily_messages=daily_messages,
        top_tags=top_tags,
    )
