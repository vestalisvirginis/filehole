# filehole
Python library to find missing files in a scheduled delivery.


## Dependencies
- Python 3.8.9 or higher
- Numpy 1.23.0
- Pandas 1.4.3
- Pyspark 3.3.0
- Holidays 0.14.2


## Install

The latest stable version can always be installed or updated via pip:
```python
$ pip install --update filehole
```


## Usage

-> frequency takes the following values: 
- for daily or weekly file delivery uses: 'C', with the required weekly_schedule' value, e.g. '1000000' for weekly file delivery on Monday.


## Limitations
- All files are expected to be at the same level.
- Current version works only with daily and weekly file delivery.


## License
This project is under the MIT License.