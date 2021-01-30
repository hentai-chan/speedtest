#!/usr/bin/env python3

import json
import logging
import os
import platform
from importlib.resources import path as resource_path
from itertools import chain
from pathlib import Path

import click
from colorama import Fore, Style

from .__init__ import package_name

#region i/o operations

def log_file_path(target_dir) -> Path:
    """
    Make a `target_dir` folder in the user's home directory, create a log
    file (if there is none, else use the existsing one) and return its path.
    """
    directory = Path.home().joinpath(target_dir)
    directory.mkdir(parents=True, exist_ok=True)
    log_file = directory.joinpath(f"{target_dir}.log")
    log_file.touch(exist_ok=True)
    return log_file

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s::%(levelname)s::%(name)s::%(message)s', datefmt='%d-%m-%y %H:%M:%S')
file_handler = logging.FileHandler(log_file_path(target_dir=package_name))
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
    with open(log_file_path(target_dir=package_name), mode='r', encoding='utf-8') as file_handler:
        log = file_handler.readlines()

        if not log:
            print_on_warning("Operation suspended: log file is empty.")
            return

        click.secho("\nLOG FILE CONTENT\n", fg='bright_magenta')

        for line in log:
            entry = line.strip('\n').split('::')
            timestamp, levelname, name, message = entry[0], entry[1], entry[2], entry[3]
            click.secho(f"[{timestamp}] ", fg='cyan', nl=False)
            click.secho(f"@{name} ", nl=False)
            tabs = '\t\t' if levelname == 'INFO' else '\t'
            click.secho(f"{levelname}{tabs}", fg=color_map[levelname], blink=(levelname=='CRITICAL'), nl=False)
            click.secho(message)

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

def write_resource(resource: str, package: str, params: dict) -> None:
    """
    Merge `params` with the content of `package` (located in `resource`) and write
    the result of this operation to disk.
    """
    config = read_resource(resource, package)
    with open(get_resource_path(package, resource), mode='w', encoding='utf-8') as file_handler:
        json.dump({**config, **params}, file_handler)

def reset_resource(resource: str, package: str) -> None:
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
