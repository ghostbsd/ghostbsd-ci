#!/usr/bin/env python
import os

packages = 'py311-requests py311-pytest'

os.system(f'pkg install -y {packages}')
