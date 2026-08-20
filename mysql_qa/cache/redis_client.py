# cache/redis_client.py
# 导入 Redis 客户端
import redis
# 导入 JSON 处理
import json
# 导入配置和日志
from base.config import config
from base.logger import logger


class RedisClient:
    def __init__(self):
        try:
            # 连接 Redis
            self.client = redis.StrictRedis(
                host=config.REDIS_HOST,
                port=config.REDIS_PORT,
                # password=config.REDIS_PASSWORD,
                db=config.REDIS_DB,
                decode_responses=True
            )
            # 验证连接是否正常
            self.client.ping()
            logger.info("Redis 连接成功")
        except redis.RedisError as e:
            # 记录连接失败，优雅降级（不崩溃）
            logger.error(f"Redis 连接失败: {e}，缓存功能将不可用")
            self.client = None

    def set_data(self, key, value, ttl=None):
        if self.client is None:
            return
        # 存储数据到 Redis
        try:
            # 存储 JSON 数据，支持可选 TTL（秒）
            if ttl:
                self.client.set(key, json.dumps(value), ex=ttl)
            else:
                self.client.set(key, json.dumps(value))
            # 记录存储成功
            logger.info(f"存储数据到 Redis: {key}")
        except redis.RedisError as e:
            # 记录存储失败
            logger.error(f"Redis 存储失败: {e}")

    def get_data(self, key):
        if self.client is None:
            return None
        # 从 Redis 获取数据
        try:
            # 获取数据
            data = self.client.get(key)
            # 返回解析后的 JSON 数据或 None
            return json.loads(data) if data else None
        except redis.RedisError as e:
            # 记录获取失败
            logger.error(f"Redis 获取失败: {e}")
            # 返回 None
            return None

    def get_answer(self, query):
        # 获取查询的缓存答案
        try:
            # 从 Redis 获取答案
            answer = self.get_data(f"answer:{query}")
            if answer:
                # 记录获取成功
                logger.info(f"从 Redis 获取答案: {query}")
                # 返回答案
                return answer
            # 返回 None
            return None
        except redis.RedisError as e:
            # 记录查询失败
            logger.error(f"Redis 查询失败: {e}")
            # 返回 None
            return None


if __name__ == '__main__':
    redis_client = RedisClient()
    # 将来从MySQL能够检索到答案，通过下面的API写入Redis
    redis_client.set_data("answer:pycharm导入模块的快捷键是什么？", "alt+enter")
    # 从Redis中通过问题检索答案
    # result = redis_client.get_data("answer:pycharm导入模块的快捷键是什么？")
    # print(result)
    # print(redis_client.get_answer("pycharm导入模块的快捷键是什么？"))
