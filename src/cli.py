#!/usr/bin/env python3

import click
from click import style

try:
    import pretty_errors
except ImportError:
    pass

from src import utils, core, speedtest
from src.__init__ import __version__, package_name


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name=package_name)
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)
    ctx.obj['CONFIG'] = utils.read_configuration('src.data', 'config.json')
    ctx.obj['SPEEDTEST'] = utils.read_configuration('src.data', 'speedtest.json')

@cli.command(help=style("Configure default application settings.", fg='bright_green'))
@click.option('--thread', type=click.INT, help=style("Set default number of speedtest threads.", fg='yellow'))
@click.option('--ping-target', type=click.STRING, help=style("Set default server ping target", fg='yellow'))
@click.option('--reset', is_flag=True, help=style("Reset all configuration settings.", fg='yellow'))
@click.option('--list', is_flag=True, help=style("List all app settings.", fg='yellow'))
@click.pass_context
def config(ctx, thread, ping_target, reset, list):
    config = ctx.obj['CONFIG']

    if thread:
        config['Thread'] = thread
        utils.write_configuration('src.data', 'config.json', config)

    if ping_target:
        config['PingTarget'] = ping_target
        utils.write_configuration('src.data', 'config.json', config)

    if reset:
        utils.reset_configuration('src.data', 'config.json')
        return

    if list:
        click.secho("\nApplication Settings", fg='bright_magenta')
        utils.print_dict('Name', 'Value', config)
