"""限流器模块

提供全局 limiter 实例，供 main.py 和路由模块共用。
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
