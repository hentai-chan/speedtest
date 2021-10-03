<p align="center">
  <a title="Project Logo">
    <img height="150" style="margin-top:15px" src="https://raw.githubusercontent.com/hentai-chan/speedtest/master/speedtest.svg">
  </a>
</p>

<h1 align="center">Speedtest Terminal Application</h1>

<p align="center">
    <a href="https://github.com/hentai-chan/speedtest" title="Release Version">
        <img src="https://img.shields.io/badge/Release-2.0.0%20-blue">
    </a>
    <a title="Supported Python Versions">
        <img src="https://img.shields.io/badge/Python-3.8%20-blue">
    </a>
    <a href="https://www.gnu.org/licenses/gpl-3.0.en.html" title="License Information" target="_blank" rel="noopener noreferrer">
        <img src="https://img.shields.io/badge/License-GPLv3-blue.svg">
    </a>
    <a href="https://archive.softwareheritage.org/browse/origin/?origin_url=https://github.com/hentai-chan/speedtest.git" title="Software Heritage Archive" target="_blank" rel="noopener noreferrer">
        <img src="https://archive.softwareheritage.org/badge/origin/https://github.com/hentai-chan/speedtest.git/">
    </a>
</p>

Speedtest is a handy terminal application for assessing the performance of your
network connectivity. It implements an alternative command line interface to
[Matt Martz' library](https://github.com/sivel/speedtest-cli).

## Setup

<details>
<summary>Installation</summary>

[pipx](https://pypa.github.io/pipx/) is the recommended way to install
Python applications in an isolated environment:

```cli
pipx install git+https://github.com/hentai-chan/speedtest.git
```

Fire up a debug build in `./venv`:

```cli
git clone https://github.com/hentai-chan/speedtest.git
cd ./speedtest
python -m venv venv/
source venv/bin/activate
pip install -e .
```

</details>

## Configuration

<details>
<summary>Customize Application Settings</summary>

**Optional**: Overwrite the default settings for `ping` and `bandwidth` tests.

```cli
speedtest config --help
```

to discover all available customizations.

Ping the target 8 times in a row.

```cli
speedtest config --count 8
```

List all application settings.

```cli
speedtest config --list
```

</details>

## Basic Usage

<details>
<summary>Command Line Usage</summary>

**[Note: You need root privileges in order to use `pythonping`.](https://github.com/alessandromaggio/pythonping#do-i-need-privileged-mode-or-root)**

Execute ping test 100 times using user-defined target and store the results to disk.

```cli
speedtest ping --count 100 --target www.hentai-chan.dev --save
```

Show the save file path.

```cli
speedtest ping --path
```

View the help page for the `bandwidth` command.

```cli
speedtest bandwidth --help
```

Run a bandwidth test with increased output verbosity and save the result to disk.
This process may take a while.

```cli
speedtest --verbose bandwidth --save
```

Reset your bandwidth history.

```cli
speedtest bandwidth --reset
```

</details>

## Report an Issue

Did something went wrong? Copy and paste the information from

```cli
speedtest log --list
```

to file a new bug report.
