"""Track process uptime."""

import time

start_time = time.time()


def process_uptime():
    return time.time() - start_time


def process_uptime_human_readable():
    t_uptime = math.floor(process_uptime())
    days = t_uptime // 86400
    hours = t_uptime % 86400 // 3600
    minutes = t_uptime % 3600 // 60
    seconds = t_uptime % 60
    if days > 0:
        if days == 1:
            p_days = f"{days} day, "
        else:
            p_days = f"{days} days, "
    else:
        p_days = ""
    if hours > 0:
        if hours == 1:
            p_hours = f"{hours} hour, "
        else:
            p_hours = f"{hours} hours, "
    else:
        p_hours = ""
    if minutes > 0:
        if minutes == 1:
            p_minutes = f"{minutes} minute, "
        else:
            p_minutes = f"{minutes} minutes, "
    else:
        p_minutes = ""
    if seconds == 1:
        p_seconds = f"{seconds} second"
    else:
        p_seconds = f"{seconds} seconds"
    return f"{p_days}{p_hours}{p_minutes}{p_seconds}"
