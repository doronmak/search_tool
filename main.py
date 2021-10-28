import csv
import os
from datetime import datetime

import typer
from database.database import create_connection
import config
import database.search_query as sq_database
import database.results as results_database


def cli(folder_path: str = typer.Argument(None, help='path of folder to search files'),
        search_pattern: str = typer.Argument(config.DEFUALT_PATTERN_FILE, help='search pattern')):
    try:
        check_inputs(folder_path, search_pattern)
        db_connection = create_connection(config.DB)
        init_database(db_connection)
        patterns, filters_as_dict, list_of_files = get_pattern_and_files(search_pattern, folder_path)
        search_id = insert_search_query_to_database(db_connection, folder_path, patterns)
        write_to_csv(filters_as_dict, folder_path)
        insert_result_to_database(db_connection, folder_path, filters_as_dict, search_id)
    except Exception as e:
        typer.echo(typer.style(e, fg=typer.colors.RED, bold=True))
        typer.echo("have a nice day!")
        exit()


def init_database(db_conn):
    sq_database.create_table(db_conn)
    results_database.create_table(db_conn)


def insert_search_query_to_database(db_conn, folder_path, pattern_dict):
    search_id = id(pattern_dict)
    date = datetime.now().strftime(config.DATE_FORMAT)
    search_query = (
        search_id, folder_path, str(pattern_dict.get('name')), str(pattern_dict.get('size')),
        str(pattern_dict.get('extension')), date)
    return sq_database.insert_search_query(db_conn, search_query)


def insert_result_to_database(db_conn, folder_path: str, files_dict: dict, query_id: int):
    for key, value in files_dict.items():
        full_path = folder_path + '\\' + key
        size = os.path.getsize(full_path)
        obj_id = id(key + str(value))
        result = (obj_id, full_path, key, str(size), str(value), query_id)
        results_database.insert_result(db_conn, result)


def check_inputs(folder_path, search_pattern):
    typer.echo(f"Hello!")
    if folder_path is None or not is_valid_path(folder_path):
        raise Exception("Folder Path not exist")
    typer.echo(f"your folder path is " + typer.style(folder_path, fg=typer.colors.GREEN))
    if not is_file_exist(search_pattern):
        raise Exception("Pattern Path Not exist")
    typer.echo(f"your search pattern file is " + typer.style(search_pattern, fg=typer.colors.GREEN))


def get_pattern_and_files(search_pattern, folder_path):
    patterns = load_patterns(search_pattern)
    filters_as_dict, list_of_files = filter_files(folder_path, patterns)
    if filters_as_dict is None:
        raise Exception("Not Found files that matching the patterns")
    list_of_files = list(list_of_files)
    typer.echo("found some matching files")
    typer.echo(list_of_files)
    return patterns, filters_as_dict, list_of_files


def is_valid_path(path: str):
    return os.path.isdir(path)


def is_file_exist(path: str):
    return os.path.isfile(path)


def load_patterns(path: str):
    with open(path, 'r', encoding="utf8") as pattern:
        rules = {}
        for line in pattern.readlines():
            line = ''.join(line.splitlines())
            line = line.replace('”', "")
            line = line.replace('"', "")
            splited_line = line.split(",")
            if rules.get(splited_line[0]):
                rules[splited_line[0]].append(splited_line[1])
            else:
                rules[splited_line[0]] = [splited_line[1]]
        return rules


# todo: split into function by pattern and extract by each file for threading and queue
def filter_files(path, patterns):
    matching_files = set()
    matching_dict = {}
    names = []
    extension = []
    size_array = []
    import os
    files = os.listdir(path)
    for file in files:
        name = is_name(file, patterns.get('name'))
        if name is not None:
            matching_files.add(name)
            if matching_dict.get(name) is not None:
                matching_dict[name].append('name')
            else:
                matching_dict[name] = ['name']
            names.append(name)

        ext = is_extension(file, patterns.get('extension'))
        if ext is not None:
            matching_files.add(ext)
            if matching_dict.get(ext) is not None:
                matching_dict[ext].append('extension')
            else:
                matching_dict[ext] = ['extension']
            extension.append(ext)
        size = is_size(path + r"\\" + file, patterns.get('size'))
        if size is not None:
            matching_files.add(size)
            if matching_dict.get(size) is not None:
                matching_dict[size].append('size')
            else:
                matching_dict[size] = ['size']
            size_array.append(size)
    if len(matching_files) == 0:
        return None
    return matching_dict, matching_files


def is_name(file_name: str, names_list: list[str]):
    if '.' in file_name:
        if file_name.split('.')[0] in names_list:
            return file_name
    if file_name in names_list:
        return file_name


def is_extension(file_name: str, patterns: list[str]):
    if '.' in file_name:
        if file_name.split('.')[1] in patterns:
            return file_name


def is_size(file_path: str, patterns: list[str]):
    size = os.path.getsize(file_path)
    if size in patterns:
        return file_path.split(r'\\')[-1]


def write_to_csv(files_dict, folder_path):
    existing_lines = None
    is_file = os.path.isfile(config.CSV_FILE)
    if is_file:
        with open(config.CSV_FILE, 'r') as file1:
            existing_lines = [line for line in csv.reader(file1, delimiter=',')]
    csv_file = open(config.CSV_FILE, "a", newline='', encoding='utf-8')
    writer = csv.writer(csv_file)
    if not is_file:
        writer.writerow(['full_path', 'file_name', 'file_size', 'matched_rules'])
    for key, value in files_dict.items():
        full_path = folder_path + '\\' + key
        size = os.path.getsize(full_path)
        row = [full_path, key, str(size), str(value)]
        if existing_lines:
            if row not in existing_lines:
                writer.writerow(row)

    csv_file.close()


if __name__ == '__main__':
    typer.run(cli)
