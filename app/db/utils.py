import pytz
from datetime import datetime
tz = pytz.timezone('Asia/Ho_Chi_Minh')

def get_current_time():
    return datetime.now().astimezone(tz)
