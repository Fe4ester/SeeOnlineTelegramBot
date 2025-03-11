import re

def is_valid_telegram_username(username):
    pattern = r'^[a-zA-Z][a-zA-Z0-9_]{4,31}$'
    return re.match(pattern, username) is not None
