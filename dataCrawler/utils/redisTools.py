from utils.connectDB import connect_redis
import traceback

def check_redis_key(key, db_number):
    redis_client = connect_redis(db=db_number)
    key_exist = redis_client.get(key)
    if key_exist:
        print(f'Same as Redis Key {key}')
        return True
    else:
        return False
    redis_client.close() 

def set_redis_key(key, db_number):
    try:
        redis_client = connect_redis(db = db_number)
        redis_client.set(key, key)
        redis_client.close()
        return True
    except:
        traceback.print_exc()
        if redis_client:
            redis_client.close()
        return False
