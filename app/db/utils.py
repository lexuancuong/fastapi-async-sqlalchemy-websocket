from datetime import datetime

import pytz

tz = pytz.timezone("Asia/Ho_Chi_Minh")


def get_current_time():
    return datetime.now().astimezone(tz)
