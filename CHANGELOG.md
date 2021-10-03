# Changelog

## Version 2.0.0 - Major Rewrite (4 October 2021)

With version 2.0.0 the implementation undergoes a radical change. Many external
dependencies have been dropped entirely (with the exception of `pythonping` which
in its newest version now requires root privileges). The plot option was also removed
from this application. You may plot this data yourself with a program of your
choice using the CSV save files which you can find here:

```cli
sudo speedtest ping --path
speedtest bandwidth --path
```

## Version 1.0.5 - Speedtest Patch (29 May 2021)

Fixes internal `speedtest` error that prematurely aborted the `bandwidth` command.

## Version 1.0.4 - Improve Log Utilities (01 March 2021)

Makes the `speedtest log --read` terminal output prettier using `rich` tables
and fixes potential permission errors with respect to the log path for non-root
users.

## Version 1.0.3 - Reset and Read Options (03 January 2021)

Adds two new flags to `ping` and `bandwidth` command, namely `--read` and `--reset`.

## Version 1.0.2 - Bug Fix (01 January 2021)

Fixed a bug that made accessing the resource files impossible.

## Version 1.0.1 - More Refined Log Options (30 January 2021)

Log-related operations are promoted to autonomous methods, see also

```cli
speedtest log --help
```

for more information.

## Version 1.0.0 - Initial Release (28 January 2021)

This is the first stable release intended for public use. In comparison to the
preview release, it adds an implementation for the plot method as well as improved
error handling. Please refer to the README file to access documentation and installation
instructions.
