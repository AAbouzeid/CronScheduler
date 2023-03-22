"""
This file contains the utility functions needed and used by the Scheduler 
"""
def convert_to_seconds(interval_str):
    timeVals = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
    unit = interval_str[-1]
    value = int(interval_str[:-1])

    try:
        mult = timeVals[unit]
        return value*mult
    
    except Exception:
        raise ValueError("Invalid time unit")