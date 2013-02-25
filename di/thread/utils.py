import re


MENTION_PATTERN = re.compile(r'@([\w]+)')

def find_mentions(text):
    return MENTION_PATTERN.findall(text)