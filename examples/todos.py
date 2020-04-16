# Jibe
# A Full-Stack Pure-Python Web Framework.
# Copyright (c) 2020 Juan Pablo Caram
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from jibe import MainApp
from jibe import Button, Input, HBox, VBox, CheckBox, Label


class TodoWidget(HBox):

    def __init__(self, label=""):
        super().__init__()

        self.checkbox = CheckBox()
        self.label = Label(label)
        self.children = [
            self.checkbox,
            self.label
        ]

    @property
    def completed(self):
        return self.checkbox.checked


class TodoListWidget(VBox):

    def __init__(self):
        super().__init__()

        self.entry = HBox()
        self.input = Input()
        self.entry.children = [
            self.input
        ]

        self.todolist = VBox()
        self.clear_button = Button("Clear Completed")

        self.children = [
            self.entry,
            self.todolist,
            self.clear_button
        ]

        # This form of attaching an event handler is for "secondary"
        # hanlers. Primary handlers are attached with @event_handler,
        # which are for events of its own widget. The primary handler
        # calls the secondary handlers. This is a secondary handler
        # beause it is an event of self.input, not self.
        self.input.register('change', self.on_add_todo)

        self.clear_button.register('click', self.on_clear_completed)

    def on_add_todo(self, source, message):
        new_todo = TodoWidget(self.input.value)
        self.todolist.children.append(new_todo)
        print(f"Added {repr(new_todo)}")

    def on_clear_completed(self, source, message):
        print(f'{self.__class__.__name__}.on_clear_completed({repr(source)}')

        for todo in self.todolist.children:
            if todo.completed:
                self.todolist.children.remove(todo)
                # TODO: This is not yet implemented in the client.


class ExampleApp(MainApp):

    def __init__(self, connection):
        super().__init__(connection)

        self.children = [
            TodoListWidget()
        ]


if __name__ == "__main__":
    ExampleApp.run(port=8881)
