def convert_to_twenty_four_hour_time_pm(time):
    hour, minute = time.split(":")
    hour_integer = int(hour)
    if hour_integer < 12:
        twenty_four_hour = str(hour_integer + 12)
    else:
        twenty_four_hour = "12"
    time = twenty_four_hour + ":" + minute
    return time


def convert_to_twenty_four_hour_time_am(time):
    hour, minute = time.split(":")
    hour_integer = int(hour)
    if hour_integer < 12:
        twenty_four_hour = str(hour_integer)
    else:
        twenty_four_hour = "0"
    time = twenty_four_hour + ":" + minute
    return time
