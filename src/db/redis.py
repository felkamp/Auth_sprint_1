import redis
from flask import Flask
from src.config import settings


redis_db = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
        )


def init_redis_db(app: Flask):
    if not hasattr(app, 'redis_db'):
        app.redis_db = redis_db
    return app.redis_db



# python shell
# from db import redis_db
#
#
# redis_db.get('key')  # Получить значение по ключу
# redis_db.set('key', 'value')  # Положить значение по ключу
# redis_db.expire('key', 10)  # Установить время жизни ключа в секундах
# # А можно последние две операции сделать за один запрос к Redis.
# redis_db.setex('key', 10, 'value')  # Положить значение по ключу с ограничением времени жизни в секундах


# Также можно атомарно работать с множеством ключей, например,
# для массового сброса сессий. Или когда в нескольких
# атомарных операциях произошёл сбой: сеть моргнула,
# маршрутизация багнула, кластер был недоступен.
# На такой случай можно использовать pipeline,
# как в транзакции в PostgreSQL.

# python shell
# import redis
# from db import redis_db
#
#
# pipeline = redis_db.pipeline()
# pipeline.setex('key', 10, 'value')
# pipeline.setex('key2', 10, 'value')
# pipeline.execute()

# or----------------------------------------------------
# import redis
# from db import redis_db
#
#
# def set_two_factor_auth_code(pipeline: redis.client.Pipeline) -> None:
#     pipeline.setex('key', 10, 'value')
#     pipeline.setex('key2', 10, 'value')
#     pipeline.setex('key3', 10, 'value')
#     pipeline.setex('key4', 10, 'value')
#
# redis_db.transaction(set_two_factor_auth_code)