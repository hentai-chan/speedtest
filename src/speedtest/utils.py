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

def log_file_path(target_dir=package_name) -> Path:
    """
    Make a `package_name` folder in the user's home directory, create a log
    file (if there is none, else use the existsing one) and return its path.
    """
    directory = Path.home().joinpath(target_dir)
    directory.mkdir(parents=True, exist_ok=True)
    log_file = directory.joinpath(f"{target_dir}.log")
    log_file.touch(exist_ok=True)
    return log_file

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s]::[%(levelname)s]::[%(name)s] - %(message)s')
file_handler = logging.FileHandler(log_file_path())
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def read_configuration(resource: str, package: str) -> dict:
    """
    Return the content of `package` (a JSON file located in `resource`) as dictionary.
    """
    with resource_path(resource, package) as resource_handler:
        with open(resource_handler, mode='r', encoding='utf-8') as file_handler:
            return json.load(file_handler)

def write_configuration(resource: str, package: str, params: dict) -> None:
    """
    Merge `params` with the content of `package` (located in `resource`) and write
    the result of this operation to disk.
    """
    config = read_configuration(resource, package)
    with resource_path(resource, package) as resource_handler:
        with open(resource_handler, mode='w', encoding='utf-8') as file_handler:
            json.dump({**config, **params}, file_handler)

def reset_configuration(resource: str, package: str) -> None:
    """
    Reset the content of `package` (a JSON file located in `resource`).
    """
    with resource_path(resource, package) as resource_handler:
        with open(resource_handler, mode='w', encoding='utf-8') as file_handler:
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
