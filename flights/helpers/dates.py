import datetime

def find_next_friday():
    today = datetime.datetime.now()
    today_num = today.strftime('%w')
    friday_num = 4
    next_friday_num = friday_num - int(today_num) + 1
    next_friday = today + datetime.timedelta(days=next_friday_num)
    return next_friday

def create_dates(rounds, first_start_date, first_end_date, format):
    dates = []
    for i in range(rounds):
        next_start = (first_start_date + datetime.timedelta(days=7*i)).strftime(format)
        next_end = (first_end_date + datetime.timedelta(days=7*i)).strftime(format)
        dates.append((next_start, next_end))
    return dates