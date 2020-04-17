# Jibe
# A Full-Stack Pure-Python Web Framework.
# Copyright (c) 2020 Juan Pablo Caram
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from jibe import Widget, MainApp, Button, Input, \
    HBox, VBox, Label, ProgressBar


class Accordion(Widget):
    """
    Example of a complex container widget.

    Its children must be put in self.body.children. This is
    a bit inconvenient. Perhaps redefine self.children...
    but that would cause a mess.
    """

    def __init__(self):

        super().__init__(
            style={
                'border': '0',
                'padding': '0',
                'margin': '0'
            }
        )

        self.titlebar = HBox(
            style={
                'border': '1px solid gray',
                'width': '100%',
            }
        )
        self.titlelabel = Label('Title')
        self.titlebar.children = [
            self.titlelabel
        ]
        self.titlebar._jshandlers['click'] = """
            this.message({event: 'click'});
        """

        # self.titlebar.local_event_handlers['click'] = self.on_bar_click

        self.body = VBox(
            style={
                'display': 'none',
                'border-style': 'solid',
                'border-color': 'gray',
                'border-width': '0px 1px 1px 1px',
                'width': '100%',
                'overflow': 'hidden'  # Solves missing part of the
                                      # side borders.
            }
        )

        self.children = [
            self.titlebar,
            self.body,
            Label('Another label')
        ]

        self.renderOnChange = False

        # TODO: This triggers the on_change() callback and
        #   tries to access self.body, which must exist,
        #   so this must be placed before it has been
        #   declared...
        self.properties['open'] = False

        self.titlebar.register('click', self.on_bar_click)

    def on_bar_click(self, source, message):
        print("On Click of titlebar")
        # self.body.css({'display': 'inherit'})
        self.open = not self.open

    def on_change(self, propname, newval, oldval):
        super().on_change(propname, newval, oldval)
        if self.open:
            self.body.css({'display': 'inherit'})
        else:
            self.body.css({'display': 'none'})

    def on_children_append(self, *args, **kwargs):
        self.body.children.append(args[0])


class ExampleApp(MainApp):

    def __init__(self, connection):
        super().__init__(connection)

        self.acc = Accordion()
        self.acc.body.children = [
            ProgressBar(),
            Label('Some label')
        ]

        self.children = [
            self.acc
        ]


if __name__ == "__main__":
    ExampleApp.run(port=8881)
