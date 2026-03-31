def fmt(seconds) -> str:
    hours, rem = divmod(seconds, 3600)
    minutes = rem // 60
    return f"{int(hours)}h {int(minutes)}m" if hours else f"{int(minutes)}m"
