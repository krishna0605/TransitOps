import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import AsyncIO

from app.core.config import get_settings

broker = RedisBroker(url=get_settings().redis_url)
broker.add_middleware(AsyncIO())
dramatiq.set_broker(broker)
