#!/usr/bin/env python
import os
import pytest
import re
import requests

# Get version from environment variable, default to '14'
version = os.environ.get('GHOSTBSD_VERSION', '14')

repos = f'/usr/local/poudriere/data/packages/ghostbsd-{version}-ghostbsd_ports/.latest/All'
raw_url = 'https://raw.githubusercontent.com/ghostbsd/ghostbsd-build/master/packages'
mate_iso_packages = requests.get(f'{raw_url}/mate').text.split()
xfce_iso_packages = requests.get(f'{raw_url}/xfce').text.split()
gershwin_iso_packages = requests.get(f'{raw_url}/gershwin').text.split()
common_iso_packages = requests.get(f'{raw_url}/common').text.split()
drivers_iso_packages = requests.get(f'{raw_url}/drivers').text.split()
iso_os_packages = [
    "os-generic-kernel",
    "os-generic-userland",
    "os-generic-userland-lib32",
    "os-generic-userland-devtools"
]
packages_list = os.listdir(repos)
useful_packages = open('tests/useful_packages', 'r').read().splitlines()


def verify_package_exists(package):
    regex = re.compile(f'({package}-)([0-9]|v[0-9]|g[0-9]).+')
    found = list(filter(regex.match, packages_list))
    assert found, f'{package} is missing'


@pytest.mark.parametrize('package', mate_iso_packages)
def test_verify_ghostbsd_packages_iso_exists(package):
    verify_package_exists(package)


@pytest.mark.parametrize('package', xfce_iso_packages)
def test_verify_ghostbsd_xfce_packages_iso_exists(package):
    verify_package_exists(package)


@pytest.mark.parametrize('package', gershwin_iso_packages)
def test_verify_ghostbsd_gershwin_packages_iso_exists(package):
    verify_package_exists(package)


@pytest.mark.parametrize('package', common_iso_packages)
def test_verify_ghostbsd_common_packages_iso_exists(package):
    verify_package_exists(package)


@pytest.mark.parametrize('package', drivers_iso_packages)
def test_verify_ghostbsd_drivers_packages_iso_exists(package):
    verify_package_exists(package)


@pytest.mark.parametrize('package', useful_packages)
def test_verify_ghostbsd_useful_packages_exists(package):
    verify_package_exists(package)
