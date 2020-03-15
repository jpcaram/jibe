# Jibe
# A Full-Stack Pure-Python Web Framework.
# Copyright (c) 2020 Juan Pablo Caram
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import tornado.ioloop
from jibe import MainApp, WebSocketHandler
from jibe import Widget, Button, Input, HBox, VBox


class ExampleApp(MainApp):
    """
    The cookie 'sessionid' is checked and created if non-existent
    by MainHandler.get(), which is invoked when the body of the page
    is requested. I believe it is not possible to set cookies via
    websockets and that is why it is done that way.

    At the time an instance of the MainApp exists, the 'sessionid'
    cookie must exist as well.
    """

    def __init__(self, connection):
        super().__init__(connection)

        self.button = Button()
        self.inbox = Input()

        self.box1 = HBox()
        self.box1.children = [
            self.button,
            self.inbox
        ]

        self.children = [self.box1]

        self.button.register('click', self.on_button_click)

    def on_button_click(self, source, message):
        print(f'{self.__class__.__name__}.on_button_click()')

        self.inbox.value = f"{self.connection.get_cookie('sessionid')}"


if __name__ == "__main__":
    app = ExampleApp.make_tornado_app()
    app.listen(8881)
    tornado.ioloop.IOLoop.current().start()
