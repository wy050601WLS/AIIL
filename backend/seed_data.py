"""测试数据种子脚本

运行方式：cd backend && python seed_data.py
会清空现有数据并重新插入完整的测试数据集。
"""

import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.database import SessionLocal
from app.models.user import User
from app.models.conversation import (
    Conversation, Message, KnowledgeCard, LearningResource, KnowledgeDocument, PromptTemplate
)
from app.utils.security import hash_password


def seed():
    """清空并重新插入测试数据"""
    db = SessionLocal()

    try:
        # Use the most recently registered user
        user = db.query(User).order_by(User.id.desc()).first()
        if not user:
            print("No user found. Please register first.")
            return

        uid = user.id
        print(f"Seeding data for user: {user.username} (id={uid})")

        # ===== Clear existing data =====
        db.query(KnowledgeDocument).filter(KnowledgeDocument.user_id == uid).delete()
        db.query(LearningResource).filter(LearningResource.user_id == uid).delete()
        db.query(KnowledgeCard).filter(KnowledgeCard.user_id == uid).delete()
        conv_ids = [c.id for c in db.query(Conversation.id).filter(Conversation.user_id == uid).all()]
        if conv_ids:
            db.query(Message).filter(Message.conversation_id.in_(conv_ids)).delete(synchronize_session=False)
        db.query(Conversation).filter(Conversation.user_id == uid).delete()
        db.commit()
        print("  [OK] Cleared old data")

        # ===== Conversations + Messages =====
        now = datetime.now()
        convos = [
            Conversation(user_id=uid, title="Python 装饰器详解", created_at=now - timedelta(days=5)),
            Conversation(user_id=uid, title="线性代数矩阵运算", created_at=now - timedelta(days=3)),
            Conversation(user_id=uid, title="英语时态总结", created_at=now - timedelta(days=1), pinned=True),
            Conversation(user_id=uid, title="Vue3 组合式 API", created_at=now - timedelta(hours=6)),
            Conversation(user_id=uid, title="SQL 查询优化", created_at=now - timedelta(hours=2)),
        ]
        for c in convos:
            db.add(c)
        db.flush()

        messages_data = [
            (convos[0].id, [
                ("user", "Python 装饰器是什么？怎么用？"),
                ("assistant", "装饰器是 Python 的一个强大特性，它本质上是一个函数，接受一个函数作为参数，返回一个新的函数。\n\n**基本语法：**\n```python\ndef my_decorator(func):\n    def wrapper(*args, **kwargs):\n        print('Before call')\n        result = func(*args, **kwargs)\n        print('After call')\n        return result\n    return wrapper\n\n@my_decorator\ndef say_hello():\n    print('Hello!')\n```\n\n**常见用途：**\n1. 日志记录\n2. 权限验证\n3. 缓存（如 `@lru_cache`）\n4. 计时器"),
                ("user", "能给一个实际项目中的例子吗？"),
                ("assistant", "当然！这是一个**接口计时装饰器**的实际例子：\n\n```python\nimport time\nimport functools\n\ndef timer(func):\n    @functools.wraps(func)\n    def wrapper(*args, **kwargs):\n        start = time.perf_counter()\n        result = func(*args, **kwargs)\n        elapsed = time.perf_counter() - start\n        print(f'{func.__name__} took {elapsed:.4f}s')\n        return result\n    return wrapper\n\n@timer\ndef fetch_data(url):\n    # 模拟 API 请求\n    time.sleep(1)\n    return {'status': 'ok'}\n```\n\n这在 FastAPI 中也很常用，可以用来记录每个接口的响应时间。"),
            ]),
            (convos[1].id, [
                ("user", "矩阵乘法怎么计算？"),
                ("assistant", "**矩阵乘法**的规则：\n\n若 A 是 m×n 矩阵，B 是 n×p 矩阵，则 C = A×B 是 m×p 矩阵。\n\n**计算方法：**\nC[i][j] = A 的第 i 行与 B 的第 j 列对应元素相乘再求和。\n\n**例子：**\n```\nA = [[1, 2],    B = [[5, 6],\n     [3, 4]]         [7, 8]]\n\nC[0][0] = 1×5 + 2×7 = 19\nC[0][1] = 1×6 + 2×8 = 22\nC[1][0] = 3×5 + 4×7 = 43\nC[1][1] = 3×6 + 4×8 = 50\n\nC = [[19, 22],\n     [43, 50]]\n```\n\n**注意：** 矩阵乘法不满足交换律，即 A×B ≠ B×A。"),
            ]),
            (convos[2].id, [
                ("user", "帮我总结英语的 8 种时态"),
                ("assistant", "**英语 8 种基本时态总结：**\n\n| 时态 | 结构 | 例句 |\n|------|------|------|\n| 一般现在时 | do/does | I study English every day. |\n| 一般过去时 | did | I studied yesterday. |\n| 一般将来时 | will do | I will study tomorrow. |\n| 现在进行时 | am/is/are doing | I am studying now. |\n| 过去进行时 | was/were doing | I was studying at 8pm. |\n| 将来进行时 | will be doing | I will be studying at 8pm. |\n| 现在完成时 | have/has done | I have studied for 2 hours. |\n| 过去完成时 | had done | I had studied before the exam. |\n\n**记忆技巧：**\n- 现在 → have/has\n- 过去 → had\n- 将来 → will\n- 进行 → be + doing"),
            ]),
            (convos[3].id, [
                ("user", "Vue3 的 setup 和 Options API 有什么区别？"),
                ("assistant", "**Composition API (setup) vs Options API：**\n\n| 特性 | Options API | Composition API |\n|------|-----------|------------------|\n| 代码组织 | 按选项分组 | 按逻辑功能分组 |\n| 复用逻辑 | Mixins | Composables |\n| TypeScript | 支持一般 | 原生支持更好 |\n| 学习曲线 | 较低 | 稍高 |\n\n**Options API 写法：**\n```js\nexport default {\n  data() { return { count: 0 } },\n  methods: { increment() { this.count++ } },\n  computed: { double: () => this.count * 2 }\n}\n```\n\n**Composition API 写法：**\n```js\nimport { ref, computed } from 'vue'\n\nconst count = ref(0)\nconst double = computed(() => count.value * 2)\nfunction increment() { count.value++ }\n```\n\n**推荐：** 新项目使用 Composition API + `<script setup>`，代码更简洁，逻辑复用更方便。"),
            ]),
            (convos[4].id, [
                ("user", "MySQL 查询很慢怎么优化？"),
                ("assistant", "**MySQL 查询优化常用方法：**\n\n1. **添加索引**\n   - 在 WHERE、JOIN、ORDER BY 的列上建索引\n   - 使用复合索引遵循最左前缀原则\n\n2. **优化 SQL 语句**\n   - 避免 `SELECT *`，只查需要的列\n   - 避免在 WHERE 中对列使用函数\n   - 用 LIMIT 限制返回行数\n\n3. **使用 EXPLAIN 分析**\n   ```sql\n   EXPLAIN SELECT * FROM users WHERE age > 18;\n   ```\n   关注 type、key、rows 字段\n\n4. **避免全表扫描**\n   - 确保查询条件能命中索引\n   - 避免 `LIKE '%keyword'`（前缀模糊）\n\n5. **分页优化**\n   ```sql\n   -- 慢\n   SELECT * FROM orders LIMIT 100000, 10;\n   -- 快\n   SELECT * FROM orders WHERE id > 100000 LIMIT 10;\n   ```\n\n6. **适当反范式化**\n   - 冗余常用字段减少 JOIN"),
            ]),
        ]

        for conv_id, msgs in messages_data:
            for i, (role, content) in enumerate(msgs):
                msg = Message(
                    conversation_id=conv_id,
                    role=role,
                    content=content,
                    created_at=now - timedelta(hours=len(msgs) - i),
                )
                db.add(msg)

        db.commit()
        print(f"  [OK] Added {len(convos)} conversations with messages")

        # ===== Knowledge Cards =====
        cards = [
            KnowledgeCard(
                user_id=uid,
                content="**装饰器模式**：Python 装饰器本质是高阶函数，接受函数作为参数，返回新函数。常用场景：日志、权限验证、缓存、计时。",
                source="conversation:1",
                tags="Python,装饰器,设计模式",
                created_at=now - timedelta(days=4),
            ),
            KnowledgeCard(
                user_id=uid,
                content="**矩阵乘法规则**：A(m×n) × B(n×p) = C(m×p)。C[i][j] = A第i行与B第j列对应元素相乘求和。矩阵乘法不满足交换律。",
                source="conversation:2",
                tags="数学,线性代数,矩阵",
                created_at=now - timedelta(days=2),
            ),
            KnowledgeCard(
                user_id=uid,
                content="**英语时态记忆法**：现在→have/has，过去→had，将来→will，进行→be+doing。四种时间 × 两种状态（一般/进行）= 8 种时态。",
                source="conversation:3",
                tags="英语,时态,语法",
                created_at=now - timedelta(days=1),
            ),
            KnowledgeCard(
                user_id=uid,
                content="**Vue3 Composition API 优势**：按逻辑功能组织代码（而非按选项），使用 Composables 复用逻辑，TypeScript 支持更好。",
                source="conversation:4",
                tags="Vue,前端,JavaScript",
                created_at=now - timedelta(hours=5),
            ),
            KnowledgeCard(
                user_id=uid,
                content="**MySQL 优化要点**：1) WHERE/JOIN 列加索引 2) 避免 SELECT * 3) 用 EXPLAIN 分析 4) 分页用 id > offset 代替 LIMIT offset",
                source="conversation:5",
                tags="MySQL,数据库,性能优化",
                created_at=now - timedelta(hours=1),
            ),
        ]
        for c in cards:
            db.add(c)
        db.commit()
        print(f"  [OK] Added {len(cards)} knowledge cards")

        # ===== Learning Resources =====
        resources = [
            LearningResource(user_id=uid, title="Python 官方文档", url="https://docs.python.org/3/",
                description="Python 3 官方文档，包含教程、标准库参考和语言参考。", category="编程", resource_type="article", tags="Python,官方文档,教程", visibility="public"),
            LearningResource(user_id=uid, title="Vue.js 3 入门教程", url="https://cn.vuejs.org/guide/introduction.html",
                description="Vue 3 官方中文指南，从零开始学习 Vue.js。", category="编程", resource_type="article", tags="Vue,前端,JavaScript", visibility="public"),
            LearningResource(user_id=uid, title="高等数学（同济版）",
                description="经典高等数学教材，涵盖极限、微积分、级数等内容。", category="数学", resource_type="book", tags="高等数学,微积分,教材", visibility="private"),
            LearningResource(user_id=uid, title="英语语法精讲", url="https://www.bbc.co.uk/learningenglish/english",
                description="BBC 英语学习频道，提供语法、词汇和听力练习。", category="英语", resource_type="course", tags="英语,语法,BBC", visibility="public"),
            LearningResource(user_id=uid, title="FastAPI 官方教程", url="https://fastapi.tiangolo.com/tutorial/",
                description="FastAPI 框架官方教程，包含路径参数、请求体、依赖注入等。", category="编程", resource_type="article", tags="FastAPI,Python,后端,API", visibility="public"),
            LearningResource(user_id=uid, title="LeetCode 算法题库", url="https://leetcode.cn/",
                description="在线算法练习平台，涵盖数组、链表、树、动态规划等。", category="编程", resource_type="tool", tags="算法,刷题,LeetCode", visibility="draft"),
            LearningResource(user_id=uid, title="3Blue1Brown 线性代数", url="https://www.bilibili.com/video/BV1ys411472E",
                description="可视化讲解线性代数本质，非常直观。", category="数学", resource_type="video", tags="线性代数,视频,3Blue1Brown", visibility="public"),
        ]
        for r in resources:
            db.add(r)
        db.commit()
        print(f"  [OK] Added {len(resources)} learning resources")

        # ===== Knowledge Documents =====
        upload_dir = os.path.join(settings.UPLOAD_DIR, "knowledge", str(uid))
        os.makedirs(upload_dir, exist_ok=True)

        doc_files = {
            "Python 基础笔记.txt": """Python 基础知识总结

1. 变量与数据类型
   - int, float, str, bool, list, dict, tuple, set
   - 动态类型，无需声明

2. 控制流
   - if/elif/else 条件判断
   - for/while 循环
   - break, continue, pass

3. 函数
   - def 定义函数
   - *args, **kwargs 可变参数
   - lambda 匿名函数

4. 面向对象
   - class 定义类
   - 继承、封装、多态
   - __init__ 构造方法

5. 常用内置函数
   - len(), range(), enumerate(), zip()
   - map(), filter(), sorted()
   - type(), isinstance(), hasattr()
""",
            "数据结构复习.txt": """数据结构复习要点

一、线性结构
  1. 数组：连续内存，O(1) 随机访问
  2. 链表：非连续，O(1) 插入删除
  3. 栈：后进先出（LIFO）
  4. 队列：先进先出（FIFO）

二、树形结构
  1. 二叉树：每个节点最多两个子节点
  2. BST：左 < 根 < 右
  3. AVL 树：自平衡二叉树
  4. 红黑树：近似平衡，插入删除效率高

三、图
  1. 邻接矩阵 vs 邻接表
  2. BFS 广度优先，DFS 深度优先
  3. Dijkstra 最短路径

四、排序算法
  1. 冒泡排序：O(n^2)
  2. 快速排序：O(n log n) 平均
  3. 归并排序：O(n log n) 稳定
  4. 堆排序：O(n log n) 原地
""",
            "SQL 常用语句.md": """# SQL 常用语句速查

## 查询
SELECT * FROM users WHERE age > 18 ORDER BY name LIMIT 10;
SELECT category, COUNT(*) FROM products GROUP BY category HAVING COUNT(*) > 5;

## 连接
SELECT u.name, o.total FROM users u INNER JOIN orders o ON u.id = o.user_id;
SELECT u.name, o.total FROM users u LEFT JOIN orders o ON u.id = o.user_id;

## 子查询
SELECT * FROM products WHERE category_id IN (SELECT id FROM categories WHERE active = 1);

## 聚合函数
COUNT(), SUM(), AVG(), MAX(), MIN()

## 窗口函数
SELECT name, score, RANK() OVER (ORDER BY score DESC) as ranking FROM students;
""",
            "英语写作模板.txt": """English Writing Templates

1. Introduction Template:
   In recent years, [topic] has become a widely discussed issue. Some people believe that [opinion A], while others argue that [opinion B]. In my opinion, [your view].

2. Body Paragraph Template:
   Firstly, [reason 1]. For example, [example]. Moreover, [reason 2]. This is because [explanation].

3. Conclusion Template:
   In conclusion, [restate your opinion]. Therefore, [suggestion/prediction].

4. Useful Phrases:
   - On the one hand... On the other hand...
   - It is widely believed that...
   - In addition / Furthermore / Moreover
   - In conclusion / To sum up / All in all
""",
        }

        docs = []
        for filename, content in doc_files.items():
            file_path = os.path.join(upload_dir, filename)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            name = os.path.splitext(filename)[0]
            ext = os.path.splitext(filename)[1].lstrip(".")
            tag = name.split(" ")[0]

            # 混合使用不同可见性
            vis_map = {"Python 基础笔记": "public", "数据结构复习": "private", "SQL 常用语句": "public", "英语写作模板": "draft"}
            doc = KnowledgeDocument(
                user_id=uid, title=name, file_type=ext,
                file_path=file_path, file_size=len(content.encode("utf-8")),
                content_text=content, tags=tag,
                visibility=vis_map.get(name, "public"),
                created_at=now - timedelta(hours=len(doc_files) - len(docs)),
            )
            docs.append(doc)
            db.add(doc)

        db.commit()
        print(f"  [OK] Added {len(docs)} knowledge documents")

        print("\nDone! All test data seeded.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
