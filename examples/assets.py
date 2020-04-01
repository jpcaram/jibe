# Jibe
# A Full-Stack Pure-Python Web Framework.
# Copyright (c) 2020 Juan Pablo Caram
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from jibe import MainApp, HTML
from pathlib import Path


class AppWithAssets(MainApp):
    """
    This Jibe Application illustrates the use custom assets (files).
    """

    assets_path = {
        'to': 'assets',
        'from': f'{Path(__file__).parent.absolute()}/data'  # Must be absolute.
    }

    def __init__(self, connection):
        super().__init__(connection)

        self.children = [
            HTML("<img src='assets/image.png'/>")
        ]


if __name__ == "__main__":
    AppWithAssets.run(8881)
