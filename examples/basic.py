# Jibe
# A Full-Stack Pure-Python Web Framework.
# Copyright (c) 2020 Juan Pablo Caram
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from jibe import MainApp, Button, Input


class ExampleApp(MainApp):
    """
    Minimal, fully-functional, example Jibe Application illustrating
    widget composition with the use of the 'children' variable and
    and handling browser events.
    """



    def __init__(self, connection):
        super().__init__(connection)

        # Nothing is sent to the browser during the construction.
        # However, as soon as we start adding children, messages
        # announcing the children are being queued for delivery.
        # Only when this widget is ready on the browser side,
        # these messages will be sent.
        # Note: This "serial" delivery is slow and probably
        # unnecessary.
        self.children = [
            Button(),
            Input(value='The value')
        ]
        self.children[0].register('click', self.on_button_click)

    def on_button_click(self, source, message):
        """
        Callback for the button's 'click' event.
        These always receive two parameter, the source widget from
        which the event originated, and the entire message sent from
        the client which contained this event.
        """
        self.children[1].value = "Hello!"


if __name__ == "__main__":
    ExampleApp.run(port=8881)
