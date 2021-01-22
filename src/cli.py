#!/usr/bin/env python3

import click
from click import style

try:
    import pretty_errors
except ImportError:
    pass

from src import utils
from src.__init__ import __version__, package_name
from src.core import square_function


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name=package_name)
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)
    ctx.obj['CONFIG'] = utils.read_configuration('src.data', 'config.json')

@cli.command(help=style("Simple test command.", fg='bright_green'))
@click.pass_context
def test(ctx):
    config = ctx.obj['CONFIG']

    # imported from config
    click.secho('\n>>> ', nl=False, fg='yellow')
    click.secho(config.get('Message', 'KeyNotFoundError'))
    
    # imported from core
    click.secho("\nFirst Ten Powers of 2", fg='bright_magenta')
    start, end = 1, 11
    utils.print_dict('X Values', 'Y Values', dict(zip(range(start, end), square_function(start, end))))
