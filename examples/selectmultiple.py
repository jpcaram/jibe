# Jibe
# A Full-Stack Pure-Python Web Framework.
# Copyright (c) 2020 Juan Pablo Caram
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import tornado.ioloop
from jibe import MainApp
from jibe import SelectMultiple


class ExampleApp(MainApp):

    def __init__(self, connection):
        super().__init__(connection)

        self.dropdown = SelectMultiple(
            options=[
                'apples',
                'banannas',
                'chocolate'
            ]
        )

        self.children = [
            self.dropdown
        ]


if __name__ == "__main__":
    ExampleApp.run(8881)
