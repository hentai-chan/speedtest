#!/usr/bin/env python3

import click
from click import style

try:
    import pretty_errors
except ImportError:
    pass

from . import utils, core
from .__init__ import __version__, package_name


@click.group(invoke_without_command=True, help=style("Speedtest is a handy terminal application for assessing the performance of your network connectivity. It implements an alternative command line interface to Matt Martz' library.", fg='bright_magenta'))
@click.version_option(version=__version__, prog_name=package_name, help=style("Read the log file", fg='yellow'))
@click.option('--read-log', is_flag=True, default=False, help=style("Read the log file", fg='yellow'))
@click.pass_context
def cli(ctx, read_log):
    ctx.ensure_object(dict)
    ctx.obj['CONFIG'] = utils.read_configuration('speedtest.data', 'config.json')
    ctx.obj['PING'] = utils.read_configuration('speedtest.data', 'ping.json')
    ctx.obj['BANDWIDTH'] = utils.read_configuration('speedtest.data', 'bandwidth.json')

    if read_log:
        click.secho("\nLOG FILE CONTENT\n", fg='bright_magenta')
        with open(utils.log_file_path(), mode='r', encoding='utf-8') as file_handler:
            log = file_handler.readlines()
            for line in log:
                text = line.strip('\n').split(' - ')
                click.secho(text[0], fg='yellow', nl=False)
                click.echo(f" - {text[1]}")

@cli.command(help=style("Configure default application settings.", fg='bright_green'))
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

@cli.command(help=style("Pings a remote host and print the responses", fg='bright_green'))
@click.option('--target', type=click.STRING, help=style("Set the remote hostname or IP address to ping", fg='yellow'))
@click.option('--count', type=click.INT, help=style("Set how many times to attempt the ping", fg='yellow'))
@click.option('--size', type=click.INT, help=style("Set the size of the entire package to send", fg='yellow'))
@click.option('--save', is_flag=True, default=False, help=style("Store results to disk.", fg='yellow'))
@click.pass_context
def ping(ctx, target, count, size, save):
    config: dict = ctx.obj['CONFIG']
    ping: dict = ctx.obj['PING']
    target: str = target or config.get('Target', 'www.google.com')
    count: int = count or config.get('Count', 4)
    size: int = size or config.get('Size', 1)

    results = core.test_ping(target, count, size)

    click.secho(f"\nPing Result", fg='bright_magenta')
    utils.print_dict('Name', 'Value', results)

    if save:
        tmp = ping.get('Results', [])
        blacklist = ['Date', 'Time', 'Ping Target', 'Country', 'ISP', 'IP']
        sanitize = lambda key, value: value.strip(' ').strip('%msMB/s') if key not in blacklist else value.strip(' ')
        tmp.append({key: sanitize(key, value) for key, value in results.items()})
        ping['Results'] = tmp
        utils.write_configuration('speedtest.data', 'ping.json', ping)

@cli.command(help=style("", fg='bright_green'))
@click.option('--threads', type=click.INT, help=style("Set the number of speedtest threads.", fg='yellow'))
@click.option('--upload', is_flag=True, default=True, help=style("Add upload stream to speedtest.", fg='yellow'))
@click.option('--download', is_flag=True, default=True, help=style("Add download stream to speedtest.", fg='yellow'))
@click.option('--save', is_flag=True, default=False, help=style("Store results to disk.", fg='yellow'))
@click.pass_context
def internet(ctx, threads, upload, download, save):
    config: dict = ctx.obj['CONFIG']
    bandwidth: dict = ctx.obj['BANDWIDTH']
    
    click.secho("Network Connection Result", fg='bright_magenta')
    results = core.test_bandwidth(threads, upload, download)
    utils.print_dict('Name', 'Value', results)

    if save:
        tmp = bandwidth.get('Results', [])
        tmp.append({key: value.strip(' ') for key, value in results.items()})
        bandwidth['Results'] = tmp
        utils.write_configuration('speedtest.data', 'bandwidth.json', bandwidth)

@cli.command(help=style("Plot internet or ping history.", fg='bright_green'))
@click.option('--name', type=click.Choice(['ping', 'bandwidth'], case_sensitive=False), help=style("Name of data set to plot.", fg='yellow'))
@click.pass_context
def plot(ctx, name):
    ping: dict = ctx.obj['PING']
    bandwidth: dict = ctx.obj['BANDWIDTH']
    click.echo(name)