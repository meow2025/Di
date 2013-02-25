import time

from flask import g


NEW_REPLY = 1
MENTION = 2

class Notification:
    def __init__(self, user_id, thread_id, type, other_user_id):
        self.user_id = user_id
        self.thread_id = thread_id
        self.type = type
        self.other_user_id = other_user_id
        self.time = int(time.time())

    def send(self):
        g.db.execute('''insert into notification(user_id, thread_id, type, 
                        other_user_id, time) values(?,?,?,?,?)''',
                     [self.user_id, self.thread_id, self.type,
                      self.other_user_id, self.time])
        g.db.commit()
