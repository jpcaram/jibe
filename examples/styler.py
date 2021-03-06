# Jibe
# A Full-Stack Pure-Python Web Framework.
# Copyright (c) 2020 Juan Pablo Caram
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from jibe import MainApp
from jibe import Button, HBox, VBox, Label


class StylerApp(MainApp):
    """
    Set CSS styles dynamically from the server. Changes the styles of
    a text upon clicking on certain buttons.
    """

    def __init__(self, connection):
        super().__init__(connection)

        topbox = VBox()
        self.button_black = Button("Black", style={'margin': '3px'})
        self.button_red = Button("Red", style={'margin': '3px'})
        self.button_large = Button("Large", style={'margin': '3px'})
        self.button_small = Button("Small", style={'margin': '3px'})
        self.buttonsbox = HBox()
        self.buttonsbox.children = [
            self.button_black,
            self.button_red,
            self.button_large,
            self.button_small
        ]

        self.labelA = Label("Label A")

        self.secbox = HBox()

        self.secbox.children = [
            self.labelA
        ]

        topbox.children = [
            self.buttonsbox, self.secbox
        ]

        self.button_black.register('click', self.on_click)
        self.button_red.register('click', self.on_click)
        self.button_large.register('click', self.on_click)
        self.button_small.register('click', self.on_click)

        self.children = [
            topbox
        ]

    def on_click(self, source, message):
        print(f'Style Swapper App on_click(): {source.label}')

        if source.label.lower() == "black":
            self.labelA.css({'color': 'black'})
        elif source.label.lower() == "red":
            self.labelA.css({'color': 'red'})
        elif source.label.lower() == "large":
            self.labelA.css({'font-size': '20px'})
        elif source.label.lower() == "small":
            self.labelA.css({'font-size': '12px'})
        else:
            print("NO SUCH BUTTON!")


if __name__ == "__main__":
    StylerApp.run(8881)
