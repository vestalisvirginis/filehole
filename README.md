# filehole
Python library to find missing files in a scheduled delivery.


Simple and quick solution to help finding missing files in a scheduled delivery, particularly when dealing with large amount of files or a long history of file delivery.


## Dependencies
- Python 3.8.9 or higher
- Numpy 1.23.0
- Holidays 0.14.2


## Install

The latest stable version can always be installed or updated via pip:
```python
$ pip install filehole
```


## Usage

```python
filehole(
    path_to_files: str,
    file_system: Globable,
    date_pattern: str,
    date_format: str,
    country: str,
    subdivision: str = None,
    start_date: str = f"{date.today().year}-01-01",
    end_date: str = date.today().strftime("%Y-%m-%d"),
    week_schedule: str = "1111100",
    frequency: str = "D",
    repetition: int = 1,
    position: int = 1,
)
```


### Parameters:

- `path_to_files` : Wild card enabled string to search for files  
- `file_system` : Modules that have a `glob` function such as `glob` in a local environment or `adls` in a cloud environment.
- `date_pattern` : Regular expression reflecting the pattern in which the date is written in files or directories.
- `date_format` : Standard date format of the date written in files or directories.
- `country` : Country name or abbreviation for the selection of the holidays calendar. For the exhaustive list of available holidays calendars, please refer to the documentation of the `holidays` python library (https://pypi.org/project/holidays/).
- `subdivision` : Province, state, ... for the selection of the holidays calendar. The available option can be found in the documentation of the `holidays` python library (https://pypi.org/project/holidays/).
-  `start_date` : Start of the search period. Format: `'%Y-%m-%d'`. Default is set to the first day of the current year.
-  `end_date` : End of the search period. Format: `'%Y-%m-%d'`. Default is set to the current date.
-  `week_schedule`: String of 7 digits of 0 and 1. 1 represents a working day and 0 a non-working day. Week starts on Monday. By default, the working week is set from Monday to Friday included -> `'1111100'`.
-  `frequency` : Takes `'D'` for daily delivery, `'W'` for weekly delivery and `'M'` for monthly delivery.
-  `repetition` : Default value: `1`. Used only for weekly and monthly file delivery. e.g.: `repetition=1` -> every week/month, `repetition=2` -> every two weeks/months...
-  `position` : Takes `1` for first business day of the month or `-1` for last business day of the month.


### Description:

Retrieve list of files from a given location.  
Extract dates from filenames.  
Create a calendar of holidays.  
Create a set of expected dates and compare them to the extracted dates.  
Return a set of missing dates.


### Example: 
- Daily file delivery for the month of July according to the french holiday calendar, assuming that files from the 12 and 13 of July are missing:
```python
> filehole(
        path_to_files="my_file_path/*.txt",  
        file_system=glob,
        date_pattern=r"[0-9]{8}",
        date_format="%Y%m%d",
        country="FR",
        start_date="2022-07-01",
        end_date="2022-07-31",
        week_schedule="1111100",
        frequency="D",
    )
> {datetime.date(2022, 7, 12), datetime.date(2022, 7, 13)}
```


## Limitations
- All files are expected to be at the same level.
- The files or the directory containing the files should contain a date in their name.
- Current version works only with daily, weekly and monthly file delivery.


## License
This project is under the MIT License.