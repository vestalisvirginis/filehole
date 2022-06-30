import re
from datetime import date, datetime
from typing import Protocol

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


def filehole(
    spark: SparkSession,
    path_to_files: str,
    file_system: Globable,
    date_pattern: str,
    date_format: str,
    country: str,
    subdivision: str = None,
    start_date: str = f"{date.today().year}-01-01",
    end_date: str = date.today().strftime("%Y-%m-%d"),
    frequency: str = "D",
    date_boundary: str = "both",
    week_schedule: str = "1111100",
) -> list:
    """
    Retrieve list of files from a given location.
    Extract dates from filenames.
    Create a calendar of holidays (optional).
    Create a list of expected dates and compare them to the extracted dates.
    Return a list of missing dates.
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

    # Build dataframe of expected dates
    expected_dates_df = spark.createDataFrame(
        pd.bdate_range(
            start_date,
            end_date,
            freq=frequency,
            weekmask=week_schedule,
            holidays=calendar.holidays,
            inclusive=date_boundary,
        ).to_frame(name="FULL_SCHEDULE")
    )

    # Check for the missing dates
    df = spark.createDataFrame(
        [[value1] for value1 in date_list],
        [
            "EXTRACTED_DATE",
        ],
    )

    return sorted(
        [
            x[0]
            for x in df.join(
                expected_dates_df,
                F.col("EXTRACTED_DATE") == F.col("FULL_SCHEDULE"),
                "right",
            )
            .filter(F.col("EXTRACTED_DATE").isNull())
            .select("FULL_SCHEDULE")
            .toLocalIterator()
        ]
    )
