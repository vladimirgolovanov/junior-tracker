from datetime import time

SLEEP_DURATION = 10 * 60 * 60
# DEPRECATED: global day boundaries. Superseded by per-child Child.day_start /
# Child.day_end. Kept only until the sleep analytics is migrated to read those
# per-child values; do not add new usages.
DAY_START = time(7, 0)
DAY_END = time(20, 0)
