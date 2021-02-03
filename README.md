<p align="center">
  <a title="Project Logo">
    <img height="150" style="margin-top:15px" src="https://raw.githubusercontent.com/hentai-chan/speedtest/master/speedtest.svg">
  </a>
</p>

<h1 align="center">Speedtest Terminal Application</h1>

<p align="center">
    <a href="https://github.com/hentai-chan/speedtest" title="Release Version">
        <img src="https://img.shields.io/badge/Release-1.0.3%20-blue">
    </a>
    <a title="Supported Python Versions">
        <img src="https://img.shields.io/badge/Python-3.8%20-blue">
    </a>
    <a href="https://www.gnu.org/licenses/gpl-3.0.en.html" title="License Information" target="_blank" rel="noopener noreferrer">
        <img src="https://img.shields.io/badge/License-GPLv3-blue.svg">
    </a>
    <a href="https://archive.softwareheritage.org/browse/origin/?origin_url=https://github.com/hentai-chan/speedtest" title="Software Heritage Archive" target="_blank" rel="noopener noreferrer">
        <img src="https://archive.softwareheritage.org/badge/origin/https://github.com/hentai-chan/speedtest.git/">
    </a>
</p>

Speedtest is a handy terminal application for assessing the performance of your
network connectivity. It implements an alternative command line interface to
[Matt Martz' library](https://github.com/sivel/speedtest-cli).

## Setup

<details>
<summary>Installation</summary>

```cli
git clone https://github.com/hentai-chan/speedtest.git
python -m venv venv/
source venv/bin/activate
pip install -e .
# test this script
speedtest --version
```

</details>

## Configuration

<details>
<summary>Customize Application Settings</summary>

**Optional**: Set default settings for `ping` and `bandwidth` tests. Run

```cli
speedtest config --help
```

to discover all available customizations.

**Example**: Set how many times to attempt the ping:

```cli
# defaults to 4
speedtest config --count=8
```

</details>

## Basic Usage

<details>
<summary>Command Line Usage</summary>

Execute ping test 100 times using `bing` as target and store the results to disk:

```cli
speedtest ping --count=100 --target=www.bing.com --save
```

View help page for `bandwidth`:

```cli
speedtest bandwidth --help
```

Plot previous bandwidth tests:

```cli
speedtest plot --history=bandwidth
```

Reset your application history:

```cli
speedtest config --reset=bandwidth
```

</details>

## Report an Issue

Did something went wrong? Copy and paste the information from

```cli
speedtest log --read
```

to file a new bug report.
