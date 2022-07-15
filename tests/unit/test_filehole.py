import pytest
import glob

import numpy as np

from datetime import datetime
from dateutil import rrule
from src.filehole import (
    FrequencyException,
    Globable,
    _get_holidays,
    _get_busday_dateutil_format,
    _daily,
    _weekly,
    _monthly,
    filehole,
)


def test_globable():
    callable(Globable.glob)


def test_get_holidays():
    rs = _get_holidays("FR", start_date="2022-07-01", end_date="2022-07-31")
    rs2 = _get_holidays("NL", start_date="2022-07-01", end_date="2022-07-31")
    isinstance(rs, list)
    isinstance(rs2, list)
    assert rs == [datetime(2022, 7, 14).date()]
    assert rs2 == []


def test_get_busday_dateutil_format():
    business_day_cal = np.busdaycalendar(weekmask="1010100")
    rs = _get_busday_dateutil_format(business_day_cal)
    isinstance(rs, list)
    assert len(rs) == 3
    assert [rrule.MO, rrule.WE, rrule.FR]


def test_daily():
    cal = np.busdaycalendar(weekmask="1111100")
    rs = _daily("2022-07-11", "2022-07-18", cal)
    isinstance(rs, list)
    assert len(rs) == 6


def test_weekly():
    cal = np.busdaycalendar(weekmask="0000011")
    rs = _weekly("2022-07-01", "2022-07-31", cal)
    isinstance(rs, list)
    assert len(rs) == 10


def test_monthly_first():
    cal1 = np.busdaycalendar(weekmask="1111100")
    cal2 = np.busdaycalendar(weekmask="0000001")
    rs1 = _monthly("2022-07-01", "2022-07-31", cal1)
    rs2 = _monthly("2022-07-01", "2022-07-31", cal2)
    isinstance(rs1, list)
    isinstance(rs2, list)
    assert rs1 == [datetime(2022, 7, 1).date()]
    assert rs2 == [datetime(2022, 7, 3).date()]


def test_monthly_last():
    cal1 = np.busdaycalendar(weekmask="1111100")
    cal2 = np.busdaycalendar(weekmask="0000001")
    rs1 = _monthly("2022-07-01", "2022-07-31", cal1, month_pos=-1)
    rs2 = _monthly("2022-07-01", "2022-07-31", cal2, month_pos=-1)
    isinstance(rs1, list)
    isinstance(rs2, list)
    assert rs1 == [datetime(2022, 7, 29).date()]
    assert rs2 == [datetime(2022, 7, 31).date()]


# weekday
# holidays/ no holidays
# missing files


def test_filehole_daily():

    rs = filehole(
        path_to_files="tests/fixtures/positive/daily_file_delivery/*.txt",
        file_system=glob,
        date_pattern=r"[0-9]{8}",
        date_format="%Y%m%d",
        country="FR",
        subdivision=None,
        start_date="2022-01-01",
        end_date="2022-07-12",
        week_schedule="1111100",
        frequency="D",
    )

    assert isinstance(rs, set)
    assert len(rs) == 0


def test_filehole_daily_with_date_in_folder_name():

    rs = filehole(
        path_to_files="tests/fixtures/positive/date_in_folder_name/*/*.txt",
        file_system=glob,
        date_pattern=r"[0-9]{4}-[0-9]{2}-[0-9]{2}",
        date_format="%Y-%m-%d",
        country="FR",
        subdivision=None,
        start_date="2022-07-01",
        end_date="2022-07-31",
        week_schedule="1111100",
        frequency="D",
    )

    assert isinstance(rs, set)
    assert len(rs) == 0


def test_filehole_daily_with_date_discrepency():

    rs = filehole(
        path_to_files="tests/fixtures/negative/date_discrepency/*/*.txt",
        file_system=glob,
        date_pattern=r"[0-9]{4}-[0-9]{2}-[0-9]{2}",
        date_format="%Y-%m-%d",
        country="FR",
        subdivision=None,
        start_date="2022-07-01",
        end_date="2022-07-31",
        week_schedule="1111100",
        frequency="D",
    )

    assert isinstance(rs, set)
    assert len(rs) == 1
    assert rs == {datetime(2022, 7, 13).date()}


def test_filehole_missing_file():

    rs = filehole(
        path_to_files="tests/fixtures/negative/daily_file_delivery/*.txt",
        file_system=glob,
        date_pattern=r"[0-9]{8}",
        date_format="%Y%m%d",
        country="FR",
        subdivision=None,
        start_date="2022-01-01",
        end_date="2022-07-12",
        week_schedule="1111100",
        frequency="D",
    )

    assert isinstance(rs, set)
    assert len(rs) == 1
    assert rs == {datetime(2022, 5, 12).date()}


def test_filehole_weekly():

    rs = filehole(
        path_to_files="tests/fixtures/positive/wednesday_weekly_file_delivery/*.txt",
        file_system=glob,
        date_pattern=r"[0-9]{8}",
        date_format="%Y%m%d",
        country="FR",
        subdivision=None,
        start_date="2022-01-01",
        end_date="2022-07-12",
        week_schedule="0010000",
        frequency="W",
    )

    assert isinstance(rs, set)
    assert len(rs) == 0


def test_filehole_monthly_first_busday():

    rs = filehole(
        path_to_files="tests/fixtures/positive/first_business_day_monthly_file_delivery/*.txt",
        file_system=glob,
        date_pattern=r"[0-9]{8}",
        date_format="%Y%m%d",
        country="FR",
        subdivision=None,
        start_date="2022-01-01",
        end_date="2022-07-12",
        week_schedule="1111100",
        frequency="M",
        position=1,
    )

    assert isinstance(rs, set)
    assert len(rs) == 0


def test_filehole_monthly_last_busday():

    rs = filehole(
        path_to_files="tests/fixtures/negative/last_business_day_monthly_file_delivery/*.txt",
        file_system=glob,
        date_pattern=r"[0-9]{8}",
        date_format="%Y%m%d",
        country="FR",
        subdivision=None,
        start_date="2022-01-01",
        end_date="2022-07-12",
        week_schedule="1111100",
        frequency="M",
        position=-1,
    )

    assert isinstance(rs, set)
    assert len(rs) == 0


def test_filehole_unknown_frequency():
    with pytest.raises(
        FrequencyException,
        match="📐 frequency accepts only the following values: 'D', 'W' and 'M'",
    ):
        rs = filehole(
            path_to_files="tests/fixtures/positive/daily_file_delivery/*.txt",
            file_system=glob,
            date_pattern=r"[0-9]{8}",
            date_format="%Y%m%d",
            country="FR",
            subdivision=None,
            start_date="2022-01-01",
            end_date="2022-07-12",
            week_schedule="1111100",
            frequency="daily",
        )


def test_typo_week_schedule():

    with pytest.raises(ValueError, match="Invalid business day weekmask string"):
        too_short = filehole(
            path_to_files="tests/fixtures/positive/daily_file_delivery/*.txt",
            file_system=glob,
            date_pattern=r"[0-9]{8}",
            date_format="%Y%m%d",
            country="FR",
            subdivision=None,
            start_date="2022-01-01",
            end_date="2022-07-12",
            week_schedule="111100",
            frequency="daily",
        )

    with pytest.raises(ValueError, match="Invalid business day weekmask string"):
        too_long = filehole(
            path_to_files="tests/fixtures/positive/daily_file_delivery/*.txt",
            file_system=glob,
            date_pattern=r"[0-9]{8}",
            date_format="%Y%m%d",
            country="FR",
            subdivision=None,
            start_date="2022-01-01",
            end_date="2022-07-12",
            week_schedule="11111100",
            frequency="daily",
        )

    with pytest.raises(ValueError, match="Invalid business day weekmask string"):
        typo = filehole(
            path_to_files="tests/fixtures/positive/daily_file_delivery/*.txt",
            file_system=glob,
            date_pattern=r"[0-9]{8}",
            date_format="%Y%m%d",
            country="FR",
            subdivision=None,
            start_date="2022-01-01",
            end_date="2022-07-12",
            week_schedule="1121100",
            frequency="daily",
        )

    with pytest.raises(
        ValueError, match="Couldn't convert object into a business day weekmask"
    ):
        wrong_format = filehole(
            path_to_files="tests/fixtures/positive/daily_file_delivery/*.txt",
            file_system=glob,
            date_pattern=r"[0-9]{8}",
            date_format="%Y%m%d",
            country="FR",
            subdivision=None,
            start_date="2022-01-01",
            end_date="2022-07-12",
            week_schedule=1111100,
            frequency="daily",
        )
