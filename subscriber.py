import redis
import json

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

def subscribe_channel(channel):
    pubsub = redis_client.pubsub()
    pubsub.subscribe(channel)
    return pubsub

def listen(pubsub):
    for message in pubsub.listen():
        if message['type'] == 'message':
            yield json.loads(message['data'])
