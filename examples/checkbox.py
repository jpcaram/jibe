# Jibe
# A Full-Stack Pure-Python Web Framework.
# Copyright (c) 2020 Juan Pablo Caram
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from jibe import MainApp
from jibe import CheckBox, Button


class ExampleApp(MainApp):

    def __init__(self, connection):
        super().__init__(connection)

        self.chk = CheckBox()
        self.btn = Button()

        self.children = [
            self.chk,
            self.btn
        ]

        self.btn.register("click", self.on_btn_click)

    def on_btn_click(self, source, message):
        """
        Callback for the button's click event.
        These always receive the source widget and the client
        message with the event. In this case source is
        self.btn.
        """
        print(f'Checked? {self.chk.checked}')
        self.chk.checked = True


if __name__ == "__main__":
    ExampleApp.run(8881)
