#!/usr/bin/env python3

import csv
import json
import logging
import os
import platform
import sys
from itertools import chain
from json.decoder import JSONDecodeError
from pathlib import Path
from types import FrameType
from typing import Dict, Union

from .__init__ import package_name
from .config import BRIGHT, CYAN, DIM, GREEN, LOGFILE, NORMAL, RED, RESET_ALL, YELLOW

#region logging and resource access

def get_config_dir() -> Path:
    """
    Return a platform-specific root directory for user configuration settings.
    """
    home = Path('/home').joinpath(os.getenv("SUDO_USER")) if '/root' == os.path.expanduser('~') else Path.home()
    return {
        'Windows': Path(os.path.expandvars('%LOCALAPPDATA%')),
        'Darwin': home.joinpath('Library').joinpath('Application Support'),
        'Linux': home.joinpath('.config')
    }[platform.system()].joinpath(package_name)

def get_resource_path(filename: Union[str, Path]) -> Path:
    """
    Return a platform-specific log file path.
    """
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    resource = config_dir.joinpath(filename)
    resource.touch(exist_ok=True)
    return resource

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s::%(levelname)s::%(lineno)d::%(name)s::%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler = logging.FileHandler(get_resource_path(LOGFILE))
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def read_json_file(filename: Union[str, Path]) -> Dict:
    """
    Read `filename` and, if this file is empty, return an empty dictionary in its place.
    """
    with open(get_resource_path(filename), mode='r', encoding='utf-8') as file_handler:
        try:
            return json.load(file_handler)
        except JSONDecodeError:
            return dict()

def write_json_file(filename: Union[str, Path], params: dict) -> None:
    """
    Save the data in `params` as a JSON file by creating an union of pre-existing data (if any).
    """
    config = read_json_file(filename)
    with open(get_resource_path(filename), mode='w', encoding='utf-8') as file_handler:
        json.dump({**config, **params}, file_handler, indent=4)
        file_handler.write('\n')

def reset_file(filename: Union[str, Path]) -> None:
    open(get_resource_path(filename), mode='w', encoding='utf-8').close()

def write_csv(filename: Union[str, Path], data: Dict[str, str]) -> None:
    with open(filename, mode='a', encoding='utf-8') as file_handler:
        writer = csv.DictWriter(file_handler, delimiter=',', lineterminator='\n', fieldnames=data.keys())
        if os.stat(filename).st_size == 0:
            writer.writeheader()
        writer.writerow(data)

#endregion logging and resource access

#region development utilities

def print_dict(title_left: str, title_right: str, table: dict) -> None:
    """
    Print a flat dictionary as table with two column titles.
    """
    table = {str(key): str(value) for key, value in table.items()}
    invert = lambda x: -x + (1 + len(max(chain(table.keys(), [title_left]), key=len)) // 8)
    tabs = lambda string: invert(len(string) // 8) * '\t'
    print('\n' + BRIGHT + GREEN + title_left + tabs(title_left) + title_right + RESET_ALL)
    print((len(title_left) * '-') + tabs(title_left) + (len(title_right) * '-'))
    for key, value in table.items():
        print(key + tabs(key) + value)
    print()

def print_on_success(message: str, verbose: bool=True) -> None:
    """
    Print a formatted success message if verbose is enabled.
    """
    if verbose:
        print(BRIGHT + GREEN + "[  OK  ]".ljust(12, ' ') + RESET_ALL + message)

def print_on_warning(message: str, verbose: bool=True) -> None:
    """
    Print a formatted warning message if verbose is enabled.
    """
    if verbose:
        print(BRIGHT + YELLOW + "[ WARNING ]".ljust(12, ' ') + RESET_ALL + message)

def print_on_error(message: str, verbose: bool=True) -> None:
    """
    Print a formatted error message if verbose is enabled.
    """
    if verbose:
        print(BRIGHT + RED + "[ ERROR ]".ljust(12, ' ') + RESET_ALL + message, file=sys.stderr)

def clear():
    """
    Reset terminal screen.
    """
    os.system('cls' if platform.system() == 'Windows' else 'clear')

#endregion development utilities
