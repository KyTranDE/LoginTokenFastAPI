import redis
import json

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

def publish_message(channel, message):
    redis_client.publish(channel, json.dumps(message))
