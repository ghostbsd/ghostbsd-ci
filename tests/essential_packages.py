#!/usr/bin/env python

import os
import pytest
import re
import requests

repos = '/zroot/poudriere/data/packages/ghostbsd-13-ghostbsd-ports/.latest/All'
raw_url = 'https://raw.githubusercontent.com/ghostbsd/ghostbsd-build' \
    '/master/packages'
mate_iso_packages = requests.get(f'{raw_url}/mate').text.split()
xfce_iso_packages = requests.get(f'{raw_url}/xfce').text.split()
packages_list = os.listdir(repos)


@pytest.mark.parametrize('package', mate_iso_packages)
def test_01_verify_ghostbsd_packages_iso_exist(package):
    regex = re.compile(f'({package}-)([0-9]|v[0-9]|g[0-9]).+')
    found = list(filter(regex.match, packages_list))
    assert found, f'{package} is missing'


@pytest.mark.parametrize('package', xfce_iso_packages)
def test_02_verify_ghostbs_xfce_packages_iso_exist(package):
    regex = re.compile(f'({package}-)([0-9]|v[0-9]|g[0-9]).+')
    found = list(filter(regex.match, packages_list))
    assert found, f'{package} is missing'
