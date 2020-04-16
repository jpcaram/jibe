# Jibe
# A Full-Stack Pure-Python Web Framework.
# Copyright (c) 2020 Juan Pablo Caram
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import setuptools
from distutils.core import setup

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name='jibe',
    version='0.1.3',
    description='Pure-Python Full-Stack Web Framework',
    long_description=long_description,
    author='Juan Pablo Caram',
    author_email='jpcaram@gmail.com',
    url='http://jibe.caram.cl',
    packages=['jibe'],
    requires=['tornado', 'jinja2', 'matplotlib', 'numpy'],
    install_requires=['tornado', 'jinja2'],
    python_requires='>=3.6',
    package_dir={'jibe': 'jibe'},
    package_data={'jibe': [
        'app.css',
        'app.js',
        'page.html',
        'lib/backbone.js',
        'lib/handlebars.js',
        'lib/jquery-1.12.4.js',
        'lib/underscore.js'
    ]}
)
