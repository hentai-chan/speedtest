#!/usr/bin/env python3

from datetime import datetime as dt
from datetime import timezone
from enum import Enum, unique

import matplotlib.pyplot as plt
import pandas as pd
from pythonping import ping

from . import utils
from .speedtest import Speedtest


@unique
class Test(Enum):
    Ping = 'ping'
    Bandwidth = 'bandwidth'

def test_ping(target: str, count: int, size: int) -> dict:
    """
    Ping a remote host and handle the responses.
    """
    now = dt.now(tz=timezone.utc)
    ping_result = ping(target=target, count=count, size=size)
    return {
        'DateTime': now.strftime('%Y-%m-%d %H:%M:%S'),
        'Ping Target': target,
        'Min. Ping': "{:6.2F}ms".format(ping_result.rtt_min_ms),
        'Max. Ping': "{:6.2F}ms".format(ping_result.rtt_max_ms),
        'Package Sent': "{:3}".format(count),
        'Package Received': "{:3.0F}".format(count - ping_result.packet_loss),
        'Package Lost': "{:3.0F}%".format(ping_result.packet_loss / count * 100)
    }

def test_bandwidth(threads: int, upload: bool, download: bool) -> dict:
    """
    Perform standard speedtest.net testing operations.
    """
    now = dt.now(tz=timezone.utc)
    test = Speedtest()
    test.get_servers()
    test.get_best_server()
    if download: test.download(threads=threads)
    if upload: test.upload(threads=threads)
    result = test.results.dict()
    return {
        'Country': result['client']['country'],
        'DateTime': now.strftime('%Y-%m-%d %H:%M:%S'),
        'ISP': result['client']['isp'],
        'IP': result['client']['ip'],
        'Download': "{:6.2F}MB/s".format(int(result['download']) / 1_000_000),
        'Upload': "{:6.2F}MB/s".format(int(result['upload']) / 1_000_000),
    }

def save(storage: dict, results: dict, test_: Test) -> None:
    """
    Save `results` data to `storage` for one of the available `test` procedures.
    """
    tmp = storage.get('Results', [])
    blacklist = ['Date', 'Time', 'Ping Target', 'Country', 'ISP', 'IP']
    sanitize = lambda key, value: value.strip(' ').strip('%msMB/s') if key not in blacklist else value.strip(' ')
    tmp.append({key: sanitize(key, value) for key, value in results.items()})
    storage['Results'] = tmp
    utils.write_resource('speedtest.data', f"{test_.value}.json", storage)

def plot_history(history: dict, ping_target: str, test_: Test) -> None:
    """
    Create a line plot by using the stored results over the entire time period.
    """
    data_frame = pd.DataFrame(history['Results'])
    format_datetime = lambda df: [dt.strptime(iso_dt_string, '%Y-%m-%d %H:%M:%S') for iso_dt_string in df['DateTime']]
    if test_ is Test.Ping:
        data_frame = data_frame[data_frame['Ping Target'] == ping_target]
        data_frame['DateTime'] = format_datetime(data_frame)
        data_frame['Min. Ping'] = list(map(float, data_frame['Min. Ping']))
        data_frame['Max. Ping'] = list(map(float, data_frame['Max. Ping']))
        axis = plt.gca()
        axis.set_xlabel('DateTime')
        axis.set_ylabel('ms')
        axis.set_title('Ping History')
        data_frame.plot(kind='line', x='DateTime', y='Min. Ping', color='blue', ax=axis, grid=True)
        data_frame.plot(kind='line', x='DateTime', y='Max. Ping', color='red', ax=axis, grid=True)
        plt.ylim(ymin=0, ymax=max(data_frame['Max. Ping'])+10)
        plt.legend(['Min. Ping', 'Max. Ping'])
    else:
        data_frame['DateTime'] = format_datetime(data_frame)
        data_frame['Download'] = list(map(float, data_frame['Download']))
        data_frame['Upload'] = list(map(float, data_frame['Upload']))
        axis = plt.gca()
        axis.set_xlabel('DateTime')
        axis.set_ylabel('MB/s')
        axis.set_title('Upload & Download History')
        data_frame.plot(kind='line', x='DateTime', y='Download', color='blue', ax=axis, grid=True)
        data_frame.plot(kind='line', x='DateTime', y='Upload', color='red', ax=axis, grid=True)
        plt.ylim(ymin=0, ymax=max(data_frame['Download'])+10)
        plt.legend(['Upload', 'Download'])
    plt.margins(0, 0)
    plt.xticks(rotation=45)
    plt.show()
