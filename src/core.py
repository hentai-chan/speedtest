#!/usr/bin/env python3

from datetime import datetime as dt
from datetime import timezone

from pythonping import ping

from src.speedtest import Speedtest


def test_ping(target: str, count: int, size: int) -> dict:
    now = dt.now(tz=timezone.utc)
    ping_result = ping(target=target, count=count, size=size)
    return {
        'Date': now.strftime('%Y-%m-%d'),
        'Time': now.strftime('%X'),
        'Ping Target': target,
        'Min. Ping': "{:6.2F}ms".format(ping_result.rtt_min_ms),
        'Max. Ping': "{:6.2F}ms".format(ping_result.rtt_max_ms),
        'Package Sent': "{:3}".format(count),
        'Package Received': "{:3.0F}".format(count - ping_result.packet_loss),
        'Package Lost': "{:3.0F}%".format(ping_result.packet_loss / count * 100)
    }

def test_bandwidth(threads: int, upload: bool, download: bool) -> dict:
    now = dt.now(tz=timezone.utc)
    test = Speedtest()
    test.get_servers()
    test.get_best_server()
    if download: test.download(threads=threads)
    if upload: test.upload(threads=threads)
    result = test.results.dict()
    return {
        'Country': result['client']['country'],
        'Date': now.strftime('%Y-%m-%d'),
        'Time': now.strftime('%X'),
        'ISP': result['client']['isp'],
        'IP': result['client']['ip'],
        'Download': "{:6.2F}MB/s".format(int(result['download']) / 1_000_000),
        'Upload': "{:6.2F}MB/s".format(int(result['upload']) / 1_000_000),
    }
