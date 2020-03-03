# Jibe
# A Full-Stack Pure-Python Web Framework.
# Copyright (c) 2020 Juan Pablo Caram
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from jibe import MainApp, HBox, CheckBox, Label


class TaskItem(HBox):

    def __init__(self, text, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.label = Label(text)
        self.chk = CheckBox()

        self.children = [self.chk, self.label]


class TestApp(MainApp):

    def __init__(self, connection):
        super().__init__(connection)

        self.children = [
            TaskItem("Hello World!")
        ]


if __name__ == "__main__":
    TestApp.run(port=8881)