#!/usr/bin/env python3

import json
from importlib.resources import path as resource_path
from itertools import chain

import click
from colorama import Fore, Style

#region i/o operations

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
    table = dict(zip(map(str, table.keys()), map(str, table.values())))
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
        click.secho(f"{Style.BRIGHT}{Fore.GREEN}{'[  OK  ]'.ljust(10, ' ')}{Style.RESET_ALL}{message}")

def print_on_error(message: str, verbose: bool=True) -> None:
    """
    Print an error message if verbose is enabled.
    """
    if verbose:
        click.secho(f"{Style.BRIGHT}{Fore.RED}{'[ ERROR ]'.ljust(10, ' ')}{Style.RESET_ALL}{message}", err=True)

#endregion
