# Jibe
# A Full-Stack Pure-Python Web Framework.
# Copyright (c) 2020 Juan Pablo Caram
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import setuptools
from distutils.core import setup

setup(
    name='jibe',
    version='0.1',
    description='Pure-Python Full-Stack Web Framework',
    author='Juan Pablo Caram',
    author_email='jpcaram@gmail.com',
    url='http://jibe.caram.cl',
    packages=['jibe'],
    requires=['tornado', 'jinja2', 'matplotlib', 'numpy'],
    install_requires=['tornado', 'jinja2']
)
