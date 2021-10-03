#!/usr/bin/env python3

import argparse
import csv
import errno
import sys
from collections import namedtuple
from time import time

from . import core, utils
from .__init__ import __version__, package_name
from .config import BANDWIDTHFILE, BRIGHT, CONFIGFILE, GREEN, LOGFILE, MAGENTA, PINGFILE, RESET_ALL, YELLOW


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version=f"%(prog)s {__version__}")
    parser.add_argument('--verbose', default=False, action='store_true', help="increase output verbosity")

    subparser = parser.add_subparsers(dest='command')

    log_parser = subparser.add_parser('log', help="interact with the application log")
    log_parser.add_argument('--path', action='store_true', help="return the log file path")
    log_parser.add_argument('--reset', action='store_true', help="purge the log file")
    log_parser.add_argument('--list', action='store_true', help='read the log file')

    config_parser = subparser.add_parser('config', help="configure default application settings")
    config_parser.add_argument('--target', type=str, nargs='?', help="set the target IP address or hostname to ping")
    config_parser.add_argument('--count', type=int, nargs='?', help="set the number of attempts")
    config_parser.add_argument('--size', type=int, nargs='?', help="set package size to send")
    config_parser.add_argument('--threads', type=int, nargs='?', help="set number of speedtest threads")
    config_parser.add_argument('--path', action='store_true', help="return the config file path")
    config_parser.add_argument('--reset', action='store_true', help='purge the config file')
    config_parser.add_argument('--list', action='store_true', help="list all user configuration")

    ping_parser = subparser.add_parser('ping', help="ping a remote host")
    ping_parser.add_argument('--target', type=str, nargs='?', help="set the target IP address or hostname to ping (default: google.com)")
    ping_parser.add_argument('--count', type=int, nargs='?', help="set the number of attempts (default: 4)")
    ping_parser.add_argument('--size', type=int, nargs='?', help="set package size to send (default: 1)")
    ping_parser.add_argument('--save', default=True, action='store_true', help="save ping results (default)")
    ping_parser.add_argument('--no-save', dest='save', action='store_false', help="don't save ping results")
    ping_parser.add_argument('--path', action='store_true', help="return the ping file path")
    ping_parser.add_argument('--reset', action='store_true', help='purge the ping file')
    ping_parser.add_argument('--list', action='store_true', help="list ping history")

    bandwidth_parser = subparser.add_parser('bandwidth', help="perform a speedtest")
    bandwidth_parser.add_argument('--threads', type=int, nargs='?', help="set number of speedtest threads")
    bandwidth_parser.add_argument('--save', default=True, action='store_true', help="save bandwidth results (default)")
    bandwidth_parser.add_argument('--no-save', dest='save', action='store_false', help="don't save bandwidth results")
    bandwidth_parser.add_argument('--path', action='store_true', help="return the ping file path")
    bandwidth_parser.add_argument('--reset', action='store_true', help='purge the ping file')
    bandwidth_parser.add_argument('--list', action='store_true', help="list ping history")

    args = parser.parse_args()
    config_data = utils.read_json_file(CONFIGFILE)

    if args.command == 'log':
        logfile = utils.get_resource_path(LOGFILE)

        if args.path:
            return logfile
        if args.reset:
            utils.reset_file(logfile)
            return
        if args.list:
            with open(logfile, mode='r', encoding='utf-8') as file_handler:
                log = file_handler.readlines()

                if not log:
                    utils.print_on_warning("Nothing to read because the log file is empty")
                    return

                parse = lambda line: line.strip('\n').split('::')
                Entry = namedtuple('Entry', 'timestamp levelname lineno name message')

                tabulate = "{:<20} {:<5} {:<6} {:<22} {:<20}".format

                print('\n' + GREEN + tabulate('Timestamp', 'Line', 'Level', 'File Name', 'Message') + RESET_ALL)

                for line in log:
                    entry = Entry(parse(line)[0], parse(line)[1], parse(line)[2], parse(line)[3], parse(line)[4])
                    print(tabulate(entry.timestamp, entry.lineno.zfill(4), entry.levelname, entry.name, entry.message))

    if args.command == 'config':
        config_file = utils.get_resource_path(CONFIGFILE)

        if args.target:
            config_data['Target'] = args.target
            utils.write_json_file(config_file, config_data)
        if args.count:
            config_data['Count'] = args.count
            utils.write_json_file(config_file, config_data)
        if args.size:
            config_data['Size'] = args.size
            utils.write_json_file(config_file, config_data)
        if args.threads:
            config_data['Threads'] = args.threads
            utils.write_json_file(config_file, config_data)
        if args.path:
            return config_file
        if args.reset:
            utils.reset_file(config_file)
            return
        if args.list:
            utils.print_dict('Name', 'Value', config_data)
            return

    if args.command == 'ping':
        ping_file = utils.get_resource_path(PINGFILE)

        if args.path:
            return ping_file
        if args.reset:
            utils.reset_file(ping_file)
            return
        if args.list:
            with open(ping_file, mode='r', encoding='utf-8') as file_handler:
                reader = csv.DictReader(file_handler)
                tabulate = "{:<20}{:<12}{:<9}{:<9}{:<13}{:<17}{:<11}".format
                print('\n' + BRIGHT + GREEN + tabulate(*reader.fieldnames) + RESET_ALL)
                for row in list(reader):
                    print(tabulate(*row.values()))
            print()
            return

        try:
            target = args.target or config_data.get('Target', 'google.com')
            count = args.count or config_data.get('Count', 4)

            ping_data = core.test_ping(target, count, args.size or config_data.get('Size', 1))

            if args.verbose:
                utils.print_dict('Name', 'Value', ping_data)

            if not args.verbose:
                print(f"Pinged {BRIGHT}{YELLOW}{target}{RESET_ALL} {count} times {BRIGHT}{MAGENTA}({RESET_ALL}Package Lost: {ping_data['PackageLost']}{BRIGHT}{MAGENTA}){RESET_ALL}")

            if args.save:
                ping_data['DateTime'] = time()
                ping_data['Target'] = target
                ping_data['PingMin'] = float(ping_data['PingMin'].strip('ms').strip(' '))
                ping_data['PingMax'] = float(ping_data['PingMax'].strip('ms').strip(' '))
                ping_data['PackageSent'] = int(ping_data['PackageSent'].strip(' '))
                ping_data['PackageReceived'] = int(ping_data['PackageReceived'].strip(' '))
                ping_data['PackageLost'] = float(ping_data['PackageLost'].strip('%').strip(' '))
                utils.write_csv(ping_file, ping_data)

        except PermissionError as perm_error:
            utils.print_on_error("You need root privileges in order to run this command.")
            utils.logger.error(str(perm_error))
        except Exception as error:
            utils.print_on_error("Something unexpected happend. The responsible authorities have already been notified.")
            utils.logger.error(str(error))

    if args.command == 'bandwidth':
        bandwidth_file = utils.get_resource_path(BANDWIDTHFILE)

        if args.path:
            return bandwidth_file
        if args.reset:
            utils.reset_file(bandwidth_file)
            return
        if args.list:
            with open(bandwidth_file, mode='r', encoding='utf-8') as file_handler:
                reader = csv.DictReader(file_handler)
                tabulate = "{:<20}{:<9}{:<15}{:<10}{:<8}{:<17}".format
                print('\n' + BRIGHT + GREEN + tabulate(*reader.fieldnames) + RESET_ALL)
                for row in list(reader):
                    print(tabulate(*row.values()))
            print()
            return

        try:
            bandwidth_data = core.test_bandwidth(args.threads or config_data.get('Threads', None))

            if args.verbose:
                utils.print_dict('Name', 'Value', bandwidth_data)

            if not args.verbose:
                print(f"Download: {BRIGHT}{YELLOW}{bandwidth_data['Download']}{RESET_ALL} | Upload: {BRIGHT}{YELLOW}{bandwidth_data['Upload']}{RESET_ALL}")

            if args.save:
                bandwidth_data['DateTime'] = time()
                bandwidth_data['Download'] = bandwidth_data['Download'].strip('MB/s').strip(' ')
                bandwidth_data['Upload'] = bandwidth_data['Upload'].strip('MB/s').strip(' ')
                utils.write_csv(bandwidth_file, bandwidth_data)

        except Exception as error:
            utils.print_on_error("Something unexpected happend. The responsible authorities have already been notified.")
            utils.logger.error(str(error))
