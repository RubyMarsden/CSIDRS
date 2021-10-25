def convert_to_twenty_four_hour_time(time):
    hour, minute = time.split(":")
    hour_integer = int(hour)
    twenty_four_hour = str(hour_integer + 6)
    time = twenty_four_hour + ":" + minute
    return time
