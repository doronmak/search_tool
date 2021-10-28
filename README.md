# Search tool

The search tool is a Python CLI tool for dealing with searching files in a folder via patterns.

## Configuration

use config file found under the project folder
```python
DB: the DB file created for sqlite3
DEFUALT_PATTERN_FILE: default file path for unentered param
DATE_FORMAT: strftime format for date saved in the database
CSV_FILE: CSV file name\path
```

## Usage

```python
main.py {FOLDER_PATH : default is None} {PATTERN_PATH : c:\pattern}
```
