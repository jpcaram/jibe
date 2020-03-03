# Jibe
# A Full-Stack Pure-Python Web Framework.
# Copyright (c) 2020 Juan Pablo Caram
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import tornado.ioloop
from jibe import MainApp
from jibe import Button, HBox, ProgressBar


class ExampleApp(MainApp):

    def __init__(self, connection):
        super().__init__(connection)

        self.button = Button()
        self.progress = ProgressBar()
        self.progress.value = 10

        self.box1 = HBox()
        self.box1.children = [
            self.button,
            self.progress
        ]

        self.children = [
            self.box1
        ]

        self.button.register('click', self.on_button_click)

    def on_button_click(self, source):
        print(f'{self.__class__.__name__}.on_button_click()')
        self.progress.value += 10


if __name__ == "__main__":
    app = ExampleApp.make_tornado_app()
    app.listen(8881)
    tornado.ioloop.IOLoop.current().start()
