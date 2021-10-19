#!/usr/bin/env python
import os

packages = 'py38-requests py38-pytest'

os.system(f'pkg install -y {packages}')
