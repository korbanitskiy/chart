from calendar import timegm


def epoch_time(x):
    """
    :param x: Datetime
    :return: time from start Epoch in milliseconds
    """
    return timegm(x.timetuple()) * 1000
