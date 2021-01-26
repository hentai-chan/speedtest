#!/usr/bin/env python3

import re
import sys

from setuptools import setup, find_packages

with open("src/speedtest/__init__.py", encoding='utf-8') as file_handler:
    lines = file_handler.read()
    version = re.search(r'__version__ = "(.*?)"', lines).group(1)
    package_name = re.search(r'package_name = "(.*?)"', lines).group(1)
    python_major = int(re.search(r'python_major = "(.*?)"', lines).group(1))
    python_minor = int(re.search(r'python_minor = "(.*?)"', lines).group(1))

try:
    assert (sys.version_info.major == python_major and sys.version_info.minor <= python_minor)
except AssertionError:
    raise RuntimeError("\033[91mPython Version %d.%d+ is required!\033[0m" % (python_major, python_minor))


print("reading dependency file")

with open("requirements/release.txt", mode='r', encoding='utf-8') as requirements:
    packages = requirements.read().splitlines()

with open("requirements/dev.txt", mode='r', encoding='utf-8') as requirements:
    dev_packages = requirements.read().splitlines()

print("reading readme file")

with open("README.md", mode='r', encoding='utf-8') as readme:
    long_description = readme.read()

print("running %s's setup routine" % package_name)

setup(
    author='hentai-chan',
    author_email="dev.hentai-chan@outlook.com",
    name=package_name,
    version=version,
    description="Speedtest is a handy terminal application for assessing the performance of your network connectivity. It implements an alternative command line interface to Matt Martz' library.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/hentai-chan/speedtest",
    project_urls={
        'Source Code': "https://github.com/hentai-chan/speedtest",
        'Bug Reports': "https://github.com/hentai-chan/speedtest/issues",
        'Changelog': "https://github.com/hentai-chan/speedtest/blob/master/CHANGELOG.md"
    },
    python_requires=">=%d.%d" % (python_major, python_minor),
    install_requires=packages,
    extra_requires={
        'dev': dev_packages[1:],
        'test': ['pytest']
    },
    include_package_data=True,
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
        entry_points={
        'console_scripts': ['%s=%s.__main__:cli' % (package_name, package_name)]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.8',
        'Operating System :: OS Independent',
        'Topic :: Terminals',
        'Topic :: Utilities',
    ],
    keywords="cli, terminal, utils, speedtest"
)

wheel_name = package_name.replace('-', '_') if '-' in package_name else package_name
print("\033[92mSetup is complete. Run 'python -m pip install dist/%s-%s-py%d-none-any.whl' to install this wheel.\033[0m" % (wheel_name, version, python_major))
