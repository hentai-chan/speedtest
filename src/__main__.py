#!/usr/bin/env python3

from src.cli import cli

if __name__ == '__main__':
    try:
        cli(obj={})
    except KeyboardInterrupt:
        pass
