#!/usr/bin/env python3

import json
import logging
import os
import platform
from collections import namedtuple
from importlib.resources import path as resource_path
from itertools import chain
from pathlib import Path

import click
from colorama import Fore, Style
from rich.console import Console
from rich.table import Table

from .__init__ import package_name

CONSOLE = Console()

#region i/o operations

def log_file_path(target_dir) -> Path:
    """
    Make a `target_dir` folder in the user's home directory, create a log
    file (if there is none, else use the existsing one) and return its path.
    """
    directory = Path(os.path.expandvars('%LOCALAPPDATA%')) if platform.system() == 'Windows' else Path().home()
    directory = directory.joinpath(f".{target_dir}")
    directory.mkdir(parents=True, exist_ok=True)
    directory.mkdir(parents=True, exist_ok=True)
    log_file = directory.joinpath(f"{target_dir}.log")
    log_file.touch(exist_ok=True)
    return log_file

LOGFILEPATH = log_file_path(target_dir=package_name)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s::%(levelname)s::%(lineno)d::%(name)s::%(message)s', datefmt='%d-%b-%y %H:%M:%S')
file_handler = logging.FileHandler(LOGFILEPATH)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def read_log() -> None:
    """
    Read color-formatted log file content from the speedtest module.
    """
    color_map = {
        'NOTSET': 'white',
        'DEBUG': 'bright_blue',
        'INFO': 'yellow',
        'WARNING': 'bright_magenta',
        'ERROR': 'red',
        'CRITICAL': 'bright_red'
    }
    with open(LOGFILEPATH, mode='r', encoding='utf-8') as file_handler:
        log = file_handler.readlines()

        if not log:
            print_on_warning("Operation suspended: log file is empty.")
            return

        table = Table(title="Log File Content")
        table.add_column('Timestamp', style='cyan')
        table.add_column('Level Name')
        table.add_column('File Name')
        table.add_column('Line Number')
        table.add_column('Message', style='green')

        parse = lambda line: line.strip('\n').split('::')
        Entry = namedtuple('Entry', 'timestamp levelname lineno name message')
        
        for entry in [Entry(parse(line)[0], parse(line)[1], parse(line)[2], parse(line)[3], parse(line)[4]) for line in log]:
            table.add_row(entry.timestamp, f"[bold {color_map[entry.levelname]}]{entry.levelname}", entry.name, entry.lineno, entry.message)
        
        CONSOLE.print(table)

def get_resource_path(package: str, resource: str) -> Path:
    """
    Get the path to a `resource` located in `package`.
    """
    with resource_path(package, resource) as resource_handler:
        return Path(resource_handler)

def read_resource(package: str, resource: str) -> dict:
    """
    Return the content of `package` (a JSON file located in `resource`) as dictionary.
    """
    with open(get_resource_path(package, resource), mode='r', encoding='utf-8') as file_handler:
        return json.load(file_handler)

def write_resource(package: str, resource: str, params: dict) -> None:
    """
    Merge `params` with the content of `package` (located in `resource`) and write
    the result of this operation to disk.
    """
    config = read_resource(package, resource)
    with open(get_resource_path(package, resource), mode='w', encoding='utf-8') as file_handler:
        json.dump({**config, **params}, file_handler)

def reset_resource(package: str, resource: str) -> None:
    """
    Reset the content of `package` (a JSON file located in `resource`).
    """
    with open(get_resource_path(package, resource), mode='w', encoding='utf-8') as file_handler:
        json.dump({}, file_handler)

#endregion

#region terminal formatting

def print_dict(title_left: str, title_right: str, table: dict) -> None:
    """
    Print a flat dictionary as table with two column titles.
    """
    table = {str(key): str(value) for key,value in table.items()}
    invert = lambda x: -x + (1 + len(max(chain(table.keys(), [title_left]), key=len)) // 8)
    tabs = lambda string: invert(len(string) // 8) * '\t'
    click.secho(f"\n{title_left}{tabs(title_left)}{title_right}", fg='bright_green')
    click.echo(f"{len(title_left) * '-'}{tabs(title_left)}{len(title_right) * '-'}")
    for key, value in table.items():
            click.echo(f"{key}{tabs(key)}{value}")
    click.echo()

def print_on_success(message: str, verbose: bool=True) -> None:
    """
    Print a success message if verbose is enabled.
    """
    if verbose:
        click.secho(f"{Style.BRIGHT}{Fore.GREEN}{'[  OK  ]'.ljust(12, ' ')}{Style.RESET_ALL}{message}")

def print_on_warning(message: str, verbose: bool=True) -> None:
    """
    Print a formatted warning message if verbose is enabled.
    """
    if verbose:
        click.secho(f"{Fore.YELLOW}{'[ WARNING ]'.ljust(12, ' ')}{Style.RESET_ALL}{message}")

def print_on_error(message: str, verbose: bool=True) -> None:
    """
    Print an error message if verbose is enabled.
    """
    if verbose:
        click.secho(f"{Style.BRIGHT}{Fore.RED}{'[ ERROR ]'.ljust(12, ' ')}{Style.RESET_ALL}{message}", err=True)

def clear():
    """
    Reset terminal screen.
    """
    os.system('cls' if platform.system() == 'Windows' else 'clear')

#endregion
