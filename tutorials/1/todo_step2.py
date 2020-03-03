# Jibe
# A Full-Stack Pure-Python Web Framework.
# Copyright (c) 2020 Juan Pablo Caram
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from jibe import MainApp, Input, Button, HBox, VBox, Label, CheckBox


class TaskItem(HBox):

    def __init__(self, text, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.label = Label(text)
        self.chk = CheckBox()

        self.children = [self.chk, self.label]


class ToDoApp(MainApp):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.input = Input()
        self.add = Button('Add')
        self.taskentry = HBox()
        self.taskentry.children = [
            self.input, self.add
        ]

        self.tasksarea = VBox()
        self.delete = Button('Delete')

        self.children = [
            self.taskentry,
            self.tasksarea,
            self.delete
        ]

        self.add.register("click", self.on_add)

    def on_add(self, source):

        self.tasksarea.children.append(
            TaskItem(self.input.value)
        )


if __name__ == "__main__":
    ToDoApp.run(port=8881)