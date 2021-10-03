#!/usr/bin/env python3

from datetime import datetime as dt
from datetime import timezone

from pythonping import ping

from .speedtest import Speedtest


def test_ping(target: str, count: int, size: int) -> dict:
    """
    Ping a remote host and return the responses data.
    """
    now = dt.now(tz=timezone.utc)
    ping_result = ping(target=target, count=count, size=size)
    return {
        'DateTime': now.strftime('%Y-%m-%d %H:%M:%S'),
        'Target': target,
        'PingMin': "{:6.2F}ms".format(ping_result.rtt_min_ms),
        'PingMax': "{:6.2F}ms".format(ping_result.rtt_max_ms),
        'PackageSent': "{:3}".format(count),
        'PackageReceived': "{:3.0F}".format(count - ping_result.packet_loss),
        'PackageLost': "{:3.0F}%".format(ping_result.packet_loss / count * 100)
    }

def test_bandwidth(threads: int) -> dict:
    """
    Perform a bandwidth test and return the response data.
    """
    now = dt.now(tz=timezone.utc)
    test = Speedtest()
    test.get_servers()
    test.get_best_server()
    test.download(threads=threads)
    test.upload(threads=threads)
    result = test.results.dict()
    return {
        'DateTime': now.strftime('%Y-%m-%d %H:%M:%S'),
        'Country': result['client']['country'],
        'IP': result['client']['ip'],
        'Download': "{:6.2F}MB/s".format(int(result['download']) / 1_000_000),
        'Upload': "{:6.2F}MB/s".format(int(result['upload']) / 1_000_000),
        'ISP': result['client']['isp'],
    }
