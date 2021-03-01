#!/usr/bin/env python3

from pprint import pprint

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
@click.version_option(version=__version__, prog_name=package_name, help=style("Show the version and exit.", fg='bright_yellow'))
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)
    ctx.obj['CONFIG'] = utils.read_resource('speedtest.data', 'config.json')
    ctx.obj['PING'] = utils.read_resource('speedtest.data', 'ping.json')
    ctx.obj['BANDWIDTH'] = utils.read_resource('speedtest.data', 'bandwidth.json')
    ctx.obj['CONSOLE'] = Console()

@cli.command(help=style("Perform log file operations.", fg='bright_green'), context_settings=CONTEXT_SETTINGS)
@click.option('--read', is_flag=True, default=False, help=style("Read the log file.", fg='bright_yellow'))
@click.option('--reset', is_flag=True, default=False, help=style("Reset all log file entries", fg='bright_yellow'))
@click.option('--path', is_flag=True, default=False, help=style("Get the log file path.", fg='bright_yellow'))
def log(read, reset, path):
    if read:
        utils.read_log()
        return

    if reset:
        open(utils.log_file_path(target_dir=package_name), mode='w', encoding='utf-8').close()
        return

    if path:
        click.echo(utils.log_file_path(target_dir=package_name))
        return

@cli.command(context_settings=CONTEXT_SETTINGS, help=style("Configure default application settings.", fg='bright_green'))
@click.option('--threads', type=click.INT, help=style("Set the number of speedtest threads.", fg='bright_yellow'))
@click.option('--target', type=click.STRING, help=style("Set the remote hostname or IP address to ping.", fg='bright_yellow'))
@click.option('--count', type=click.INT, help=style("Set how many times to attempt the ping.", fg='bright_yellow'))
@click.option('--size', type=click.INT, help=style("Set the size of the entire package to send.", fg='bright_yellow'))
@click.option('--reset', type=click.Choice(['config', 'ping', 'bandwidth'], case_sensitive=False), help=style("Reset all configuration or speedtest entries.", fg='bright_yellow'))
@click.option('--list', is_flag=True, help=style("List all app settings.", fg='bright_yellow'))
@click.pass_context
def config(ctx, threads, target, count, size, reset, list):
    config: dict = ctx.obj['CONFIG']

    if threads:
        config['Threads'] = threads
        utils.write_resource('speedtest.data', 'config.json', config)

    if target:
        config['Target'] = target
        utils.write_resource('speedtest.data', 'config.json', config)

    if count:
        config['Count'] = count
        utils.write_resource('speedtest.data', 'config.json', config)

    if size:
        config['Size'] = size
        utils.write_resource('speedtest.data', 'config.json', config)

    if reset:
        utils.reset_resource('speedtest.data', f"{reset}.json")
        return

    if list:
        click.secho("\nApplication Settings", fg='bright_magenta')
        utils.print_dict('Name', 'Value', config)
        return

@cli.command(context_settings=CONTEXT_SETTINGS, help=style("Ping a remote host and get the response data.", fg='bright_green'))
@click.option('--target', type=click.STRING, help=style("Set the remote hostname or IP address to ping.", fg='bright_yellow'))
@click.option('--count', type=click.INT, help=style("Set how many times to attempt the ping.", fg='bright_yellow'))
@click.option('--size', type=click.INT, help=style("Set the size of the entire package to send.", fg='bright_yellow'))
@click.option('--reset', is_flag=True, help=style("Wipe out your ping save file.", fg='bright_yellow'))
@click.option('--read', is_flag=True, default=False, help=style("Read your ping save file.", fg='bright_yellow'))
@click.option('--save/--no-save', is_flag=True, default=False, help=style("Store results to disk.", fg='bright_yellow'))
@click.pass_context
def ping(ctx, target, count, size, reset, read, save):
    config: dict = ctx.obj['CONFIG']
    ping: dict = ctx.obj['PING']
    console: Console = ctx.obj['CONSOLE']
    target: str = target or config.get('Target', 'www.google.com')
    count: int = count or config.get('Count', 4)
    size: int = size or config.get('Size', 1)

    if reset:
        utils.reset_resource('speedtest.data', 'ping.json')
        return

    if read:
        pprint(ping, indent=2)
        return

    try:
        with console.status('Running bandwidth test . . .', spinner='dots3') as _:        
            results = core.test_ping(target, count, size)

        click.secho(f"\nPing Results", fg='bright_magenta')
        utils.print_dict('Name', 'Value', results)

        if save:
            core.save(ping, results, Test.Ping)
    except Exception as exception:
        utils.logger.critical(f"The application failed to run a ping test: {exception}")

@cli.command(context_settings=CONTEXT_SETTINGS, help=style("Perform standard speedtest.net testing operations.", fg='bright_green'))
@click.option('--threads', type=click.INT, help=style("Set the number of speedtest threads.", fg='bright_yellow'))
@click.option('--upload/--no-upload', is_flag=True, default=True, help=style("Add upload stream to speedtest.", fg='bright_yellow'))
@click.option('--download/--no-download', is_flag=True, default=True, help=style("Add download stream to speedtest.", fg='bright_yellow'))
@click.option('--reset', is_flag=True, help=style("Wipe out your bandwidth save file.", fg='bright_yellow'))
@click.option('--read', is_flag=True, default=False, help=style("Read your bandwidth save file.", fg='bright_yellow'))
@click.option('--save/--no-save', is_flag=True, default=False, help=style("Store results to disk.", fg='bright_yellow'))
@click.pass_context
def bandwidth(ctx, threads, upload, download, reset, read, save):
    bandwidth: dict = ctx.obj['BANDWIDTH']
    console: Console = ctx.obj['CONSOLE']

    if reset:
        utils.reset_resource('speedtest.data', 'bandwidth.json')
        return

    if read:
        pprint(bandwidth, indent=2)
        return
    
    try:
        with console.status('Running bandwidth test . . .', spinner='dots3') as _:
            results = core.test_bandwidth(threads, upload, download)

        click.secho("\nBandwidth Results", fg='bright_magenta')
        utils.print_dict('Name', 'Value', results)

        if save:
            core.save(bandwidth, results, Test.Bandwidth)
    except Exception as exception:
        utils.logger.critical(f"The application failed to run a bandwidth test: {exception}")

@cli.command(context_settings=CONTEXT_SETTINGS, help=style("Plot bandwidth or ping history.", fg='bright_green'))
@click.option('--history', type=click.Choice(['ping', 'bandwidth'], case_sensitive=False), help=style("Name of data set to plot.", fg='bright_yellow'))
@click.pass_context
def plot(ctx, history):
    config: dict = ctx.obj['CONFIG']
    ping: dict = ctx.obj['PING']
    bandwidth: dict = ctx.obj['BANDWIDTH']
    console: Console = ctx.obj['CONSOLE']
    target: str = config.get('Target', 'www.google.com')

    if not history:
        utils.print_on_warning("You need to specify an plot option. Run 'speedtest plot --help' to view this command's help page.")
        return

    try:
        with console.status('Plotting data . . .', spinner='dots3') as _:
            core.plot_history(ping if history=='ping' else bandwidth, target, Test(history))
    except KeyError:
        utils.logger.warning(f"Attempted plot invocation with history={history}")
        utils.print_on_error(f"No data to plot available. Run 'speedtest {history} --save' to store results to disk.")
    except Exception as exception:
        utils.logger.critical(f"Something went wrong while trying to plot the history for {history}: {exception}")
