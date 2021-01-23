#!/usr/bin/env python3

import click
from click import style

try:
    import pretty_errors
except ImportError:
    pass

from src import utils, core
from src.__init__ import __version__, package_name


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name=package_name)
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)
    ctx.obj['CONFIG'] = utils.read_configuration('src.data', 'config.json')
    ctx.obj['PING'] = utils.read_configuration('src.data', 'ping.json')
    ctx.obj['BANDWIDTH'] = utils.read_configuration('src.data', 'bandwidth.json')

@cli.command(help=style("Configure default application settings.", fg='bright_green'))
@click.option('--threads', type=click.INT, help=style("Set the number of speedtest threads.", fg='yellow'))
@click.option('--target', type=click.STRING, help=style("Set the remote hostname or IP address to ping.", fg='yellow'))
@click.option('--count', type=click.INT, help=style("Set how many times to attempt the ping.", fg='yellow'))
@click.option('--size', type=click.INT, help=style("Set the size of the entire package to send.", fg='yellow'))
@click.option('--reset', type=click.Choice(['config', 'ping', 'bandwidth'], case_sensitive=False), help=style("Reset all configuration or speedtest entries.", fg='yellow'))
@click.option('--list', is_flag=True, help=style("List all app settings.", fg='yellow'))
@click.pass_context
def config(ctx, threads, target, count, size, reset, list):
    config_file: dict = ctx.obj['CONFIG']

    if threads:
        config_file['Threads'] = threads
        utils.write_configuration('src.data', 'config.json', config_file)

    if target:
        config_file['Target'] = target
        utils.write_configuration('src.data', 'config.json', config_file)

    if count:
        config_file['Count'] = count
        utils.write_configuration('src.data', 'config.json', config_file)

    if size:
        config_file['Size'] = size
        utils.write_configuration('src.data', 'config.json', config_file)

    if reset:
        utils.reset_configuration('src.data', f"{reset}.json")
        return

    if list:
        click.secho("\nApplication Settings", fg='bright_magenta')
        utils.print_dict('Name', 'Value', config_file)

@cli.command(help=style("Pings a remote host and print the responses", fg='bright_green'))
@click.option('--target', type=click.STRING, help=style("Set the remote hostname or IP address to ping", fg='yellow'))
@click.option('--count', type=click.INT, help=style("Set how many times to attempt the ping", fg='yellow'))
@click.option('--size', type=click.INT, help=style("Set the size of the entire package to send", fg='yellow'))
@click.option('--save', is_flag=True, default=False, help=style("Store results to disk.", fg='yellow'))
@click.pass_context
def ping(ctx, target, count, size, save):
    config_file: dict = ctx.obj['CONFIG']
    ping_file: dict = ctx.obj['PING']
    target: str = target or config_file.get('Target', 'www.google.com')
    count: int = count or config_file.get('Count', 4)
    size: int = size or config_file.get('Size', 1)

    results = core.test_ping(target, count, size)

    click.secho(f"\nPing Result", fg='bright_magenta')
    utils.print_dict('Name', 'Value', results)

    if save:
        tmp = ping_file.get('Results', [])
        tmp.append({key: value.strip(' ') for key, value in results.items()})
        ping_file['Results'] = tmp
        utils.write_configuration('src.data', 'ping.json', ping_file)

@cli.command(help=style("", fg='bright_green'))
@click.option('--threads', type=click.INT, help=style("Set the number of speedtest threads.", fg='yellow'))
@click.option('--upload', is_flag=True, default=True, help=style("Add upload stream to speedtest.", fg='yellow'))
@click.option('--download', is_flag=True, default=True, help=style("Add download stream to speedtest.", fg='yellow'))
@click.option('--save', is_flag=True, default=False, help=style("Store results to disk.", fg='yellow'))
@click.pass_context
def internet(ctx, threads, upload, download, save):
    config_file: dict = ctx.obj['CONFIG']
    bandwidth_file: dict = ctx.obj['BANDWIDTH']
    
    # click.echo("\033[A\033[A")
    click.secho("Network Connection Result", fg='bright_magenta')
    results = core.test_bandwidth(threads, upload, download)
    utils.print_dict('Name', 'Value', results)

    if save:
        tmp = bandwidth_file.get('Results', [])
        tmp.append({key: value.strip(' ') for key, value in results.items()})
        bandwidth_file['Results'] = tmp
        utils.write_configuration('src.data', 'bandwidth.json', bandwidth_file)

@cli.command(help=style("Plot internet or ping history.", fg='bright_green'))
@click.option('--name', type=click.Choice(['ping', 'bandwidth'], case_sensitive=False), help=style("Name of data set to plot.", fg='yellow'))
@click.pass_context
def plot(ctx, name):
    ping_file: dict = ctx.obj['PING']
    bandwidth_file: dict = ctx.obj['BANDWIDTH']
    click.echo(name)