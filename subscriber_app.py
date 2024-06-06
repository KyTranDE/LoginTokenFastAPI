from subscriber import subscribe_channel, listen
import emoji
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

channel = 'expired_accounts'
pubsub = subscribe_channel(channel)

print(f"Listening for messages on channel '{channel}'...")

log_dir = './log'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

for message in listen(pubsub):
    with open(os.path.join(log_dir, 'logRedis.txt'), 'a', encoding='utf-8') as f:
        f.write(f"{emoji.emojize(':cross_mark:')} {message}\n")
