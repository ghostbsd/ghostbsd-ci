#!/usr/bin/env python
import os

packages = 'py39-requests py39-pytest'

os.system(f'pkg install -y {packages}')
