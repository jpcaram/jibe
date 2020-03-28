# Jibe
# A Full-Stack Pure-Python Web Framework.
# Copyright (c) 2020 Juan Pablo Caram
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from jibe import MainApp, Image
import base64


class ExampleApp(MainApp):

    def __init__(self, connection):
        super().__init__(connection)

        with open('data/image.png', 'rb') as img:
            data = base64.encodebytes(img.read()).decode('utf-8')

        img = Image()
        img.data = data
        self.children = [img]


if __name__ == "__main__":
    ExampleApp.run(8881)