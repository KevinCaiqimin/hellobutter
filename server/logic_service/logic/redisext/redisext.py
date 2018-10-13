class RedisExt:
    @staticmethod
    def optimLock(Redis, key, seconds):
        result = Redis.setnx(key, 1)
        if result is None:
            return False
        if result == 0:
            return False
        if seconds > 0:
            Redis.expire(key, seconds)
        return True

    @staticmethod
    def optimUnlock(Redis, key):
        Redis.delete(key)

    @staticmethod
    def set(Redis, key, value, seconds):
        pipe = Redis.pipeline()
        pipe.set(key, value)
        pipe.expire(seconds)
        pipe.execute()