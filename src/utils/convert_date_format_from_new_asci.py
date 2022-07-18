from datetime import datetime


def standardise_date_format(date):
    if validate_date(date):
        return date
    else:
        day = str.split(date, "-")[0]
        month = convert_to_numerical_month(str.split(date, "-")[1])
        year = "20" + str.split(date, "-")[2]
        standardised_date = day + "/" + month + "/" + year
        return standardised_date


def validate_date(d):
    try:
        datetime.strptime(d, '%d/%m/%Y')
        return True
    except ValueError:
        return False


def convert_to_numerical_month(alphabetical_month):
    months = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
              "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
    for month in months.keys():
        if month == alphabetical_month:
            return months[month]
