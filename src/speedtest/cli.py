#!/usr/bin/env python3

import click
from click import style
from rich.console import Console

try:
    import pretty_errors
except ImportError:
    pass

from . import core, utils
from .__init__ import __version__, package_name
from .core import Test

CONTEXT_SETTINGS = dict(max_content_width=120)

@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS, help=style("Speedtest is a handy terminal application for assessing the performance of your network connectivity. It implements an alternative command line interface to Matt Martz' library.", fg='bright_magenta'))
@click.version_option(version=__version__, prog_name=package_name, help=style("Read the log file", fg='yellow'))
@click.option('--read-log', is_flag=True, default=False, help=style("Read the log file", fg='yellow'))
@click.pass_context
def cli(ctx, read_log):
    ctx.ensure_object(dict)
    ctx.obj['CONFIG'] = utils.read_configuration('speedtest.data', 'config.json')
    ctx.obj['PING'] = utils.read_configuration('speedtest.data', 'ping.json')
    ctx.obj['BANDWIDTH'] = utils.read_configuration('speedtest.data', 'bandwidth.json')
    ctx.obj['CONSOLE'] = Console()

    if read_log:
        utils.read_log()

@cli.command(context_settings=CONTEXT_SETTINGS, help=style("Configure default application settings.", fg='bright_green'))
@click.option('--threads', type=click.INT, help=style("Set the number of speedtest threads.", fg='yellow'))
@click.option('--target', type=click.STRING, help=style("Set the remote hostname or IP address to ping.", fg='yellow'))
@click.option('--count', type=click.INT, help=style("Set how many times to attempt the ping.", fg='yellow'))
@click.option('--size', type=click.INT, help=style("Set the size of the entire package to send.", fg='yellow'))
@click.option('--reset', type=click.Choice(['config', 'ping', 'bandwidth'], case_sensitive=False), help=style("Reset all configuration or speedtest entries.", fg='yellow'))
@click.option('--list', is_flag=True, help=style("List all app settings.", fg='yellow'))
@click.pass_context
def config(ctx, threads, target, count, size, reset, list):
    config: dict = ctx.obj['CONFIG']

    if threads:
        config['Threads'] = threads
        utils.write_configuration('speedtest.data', 'config.json', config)

    if target:
        config['Target'] = target
        utils.write_configuration('speedtest.data', 'config.json', config)

    if count:
        config['Count'] = count
        utils.write_configuration('speedtest.data', 'config.json', config)

    if size:
        config['Size'] = size
        utils.write_configuration('speedtest.data', 'config.json', config)

    if reset:
        utils.reset_configuration('speedtest.data', f"{reset}.json")
        return

    if list:
        click.secho("\nApplication Settings", fg='bright_magenta')
        utils.print_dict('Name', 'Value', config)
        return

@cli.command(context_settings=CONTEXT_SETTINGS, help=style("Ping a remote host and get the response data.", fg='bright_green'))
@click.option('--target', type=click.STRING, help=style("Set the remote hostname or IP address to ping", fg='yellow'))
@click.option('--count', type=click.INT, help=style("Set how many times to attempt the ping", fg='yellow'))
@click.option('--size', type=click.INT, help=style("Set the size of the entire package to send", fg='yellow'))
@click.option('--save', is_flag=True, default=False, help=style("Store results to disk.", fg='yellow'))
@click.pass_context
def ping(ctx, target, count, size, save):
    config: dict = ctx.obj['CONFIG']
    ping: dict = ctx.obj['PING']
    console: Console = ctx.obj['CONSOLE']
    target: str = target or config.get('Target', 'www.google.com')
    count: int = count or config.get('Count', 4)
    size: int = size or config.get('Size', 1)

    with console.status('Running bandwidth test . . .', spinner='dots3') as _:
        results = core.test_ping(target, count, size)

    click.secho(f"\nPing Result", fg='bright_magenta')
    utils.print_dict('Name', 'Value', results)

    if save:
        core.save(ping, results, Test.Ping)

@cli.command(context_settings=CONTEXT_SETTINGS, help=style("Perform standard speedtest.net testing operations.", fg='bright_green'))
@click.option('--threads', type=click.INT, help=style("Set the number of speedtest threads.", fg='yellow'))
@click.option('--upload', is_flag=True, default=True, help=style("Add upload stream to speedtest.", fg='yellow'))
@click.option('--download', is_flag=True, default=True, help=style("Add download stream to speedtest.", fg='yellow'))
@click.option('--save', is_flag=True, default=False, help=style("Store results to disk.", fg='yellow'))
@click.pass_context
def bandwidth(ctx, threads, upload, download, save):
    config: dict = ctx.obj['CONFIG']
    bandwidth: dict = ctx.obj['BANDWIDTH']
    console: Console = ctx.obj['CONSOLE']
    
    with console.status('Running bandwidth test . . .', spinner='dots3') as _:
        results = core.test_bandwidth(threads, upload, download)

    click.secho("\nNetwork Connection Result", fg='bright_magenta')
    utils.print_dict('Name', 'Value', results)

    if save:
        core.save(bandwidth, results, Test.Bandwidth)

@cli.command(context_settings=CONTEXT_SETTINGS, help=style("Plot internet or ping history.", fg='bright_green'))
@click.option('--history', type=click.Choice(['ping', 'bandwidth'], case_sensitive=False), help=style("Name of data set to plot.", fg='yellow'))
@click.pass_context
def plot(ctx, history):
    ping: dict = ctx.obj['PING']
    bandwidth: dict = ctx.obj['BANDWIDTH']
