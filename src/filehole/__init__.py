import re
from datetime import date, datetime
from typing import Protocol
from dateutil.rrule import (
    rrule,
    DAILY,
    WEEKLY,
    MONTHLY,
    YEARLY,
    MO,
    TU,
    WE,
    TH,
    FR,
    SA,
    SU,
)
from dateutil.parser import parse

import holidays
import numpy as np
import pandas as pd
import pyspark.sql.functions as F
from pyspark.sql import SparkSession


class Globable(Protocol):
    def glob(str):
        pass


def _get_holidays(
    country: str,
    subdivision: str = None,
    start_date: str = f"{date.today().year}-01-01",
    end_date: str = date.today().strftime("%Y-%m-%d"),
) -> list:
    """Get the list of holidays for a given country or state between a range of dates."""

    years_of_interest = list(
        range(
            date.fromisoformat(start_date).year, date.fromisoformat(end_date).year + 1
        )
    )
    country_cal = getattr(holidays, country)

    return [date for date in country_cal(subdiv=subdivision, years=years_of_interest)]


def _get_busday_dateutil_format(busday_schedule: np.busdaycalendar) -> list:
    '''
    Return a list of busday for use with rrule function.
    '''

    dateutil_weekdays = np.array([MO, TU, WE, TH, FR, SA, SU])

    return dateutil_weekdays[busday_schedule.weekmask].tolist()


def _daily(strt_date: str, end_date: str, business_days: np.busdaycalendar) -> list:
    """
    Return a list of datetimes between the start and the end date based on given business days.
    """

    return [
        d.date()
        for d in rrule(
            DAILY,
            dtstart=parse(strt_date),
            until=parse(end_date),
            byweekday=_get_busday_dateutil_format(business_days),
        )
    ]


def _weekly(
    strt_date: str, end_date: str, business_days: np.busdaycalendar, repeat: int = 1
) -> list:
    """
    Return a list of datetimes between the start and the end date based on given business days (one or several days can be selected) and repeat interval (by default, delivery event repeat every weeks for the selected days).
    """
    return [
        d.date()
        for d in rrule(
            WEEKLY,
            dtstart=parse(strt_date),
            until=parse(end_date),
            byweekday=_get_busday_dateutil_format(business_days),
            interval=repeat,
        )
    ]


def _monthly(
    strt_date: str,
    end_date: str,
    business_days: np.busdaycalendar,
    repeat: int = 1,
    month_pos: int = 1,
) -> list:
    """
    Return a list of datetimes between the start and the end date based on given business days and repeat interval (by default, every months). The `month_pos` allows the user to select either the first `1`
    or the last `-1` business day of the month (default behaviour, first business day of the month is returned).
    """
    return [
        d.date()
        for d in rrule(
            MONTHLY,
            dtstart=parse(strt_date),
            until=parse(end_date),
            byweekday=_get_busday_dateutil_format(business_days),
            interval=repeat,
            bysetpos=month_pos,
        )
    ]


def filehole(
    path_to_files: str,
    file_system: Globable,
    date_pattern: str,
    date_format: str,
    country: str,
    subdivision: str = None,
    start_date: str = f"{date.today().year}-01-01",
    end_date: str = date.today().strftime("%Y-%m-%d"),
    week_schedule: str = "1111100",
    frequency: str = 'D',
    repetition: int =1,
    position: int = 1,
) -> list: 
    """
    Retrieve list of files from a given location.
    Extract dates from filenames.
    Create a calendar of holidays (optional).
    Create a set of expected dates and compare them to the extracted dates.
    Return a set of missing dates.
    """

    # Extract dates from files or folder names.
    file_list = file_system.glob(path_to_files)

    date_str_list = [
        date[-1] for date in [re.findall(date_pattern, file) for file in file_list]
    ]
    date_list = list(
        map(
            lambda date_str: datetime.strptime(date_str, date_format).date(),
            date_str_list,
        )
    )

    # Build a calendar based on start/end dates, week and holiday schedule.
    holidays_list = _get_holidays(country, subdivision, start_date, end_date)
    calendar = np.busdaycalendar(weekmask=week_schedule, holidays=holidays_list)

    # Missing dates
    if frequency == 'D':
        return set(_daily(start_date, end_date, calendar)).difference(set(calendar.holidays.tolist()).union(set(date_list)))
    elif frequency == 'W':
        return set(_weekly(start_date, end_date, calendar, repetition)).difference(set(calendar.holidays.tolist()).union(set(date_list)))
    elif frequency == 'M':
        return set(_monthly(start_date, end_date, calendar, repetition, position)).difference(set(calendar.holidays.tolist()).union(set(date_list)))
    else:
        return f'Frequency error'