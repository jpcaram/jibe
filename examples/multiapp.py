# Jibe
# A Full-Stack Pure-Python Web Framework.
# Copyright (c) 2020 Juan Pablo Caram
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from jibe import MainApp, Button, Input, CheckBox, \
    Redirect, MultiApp


class ExampleAppA(MainApp):

    def __init__(self, connection):
        super().__init__(connection)

        self.btn_go2b = Button(label='Go to B')
        self.btn = Button()
        self.input = Input(value='The value')
        self.redir = Redirect()

        self.children = [
            self.btn_go2b,
            self.btn,
            self.input,
            self.redir
        ]
        self.btn.register('click', self.on_button_click)
        self.btn_go2b.register("click", self.on_go2b)

    def on_button_click(self, source, message):
        self.input.value = "Hello!"

    def on_go2b(self, source, message):
        self.redir.redirect('/b')


class ExampleAppB(MainApp):

    def __init__(self, connection):
        super().__init__(connection)
        self.btn_go2a = Button(label='Go to A')
        self.chk = CheckBox()
        self.btn = Button()
        self.redir = Redirect()
        self.children = [
            self.btn_go2a,
            self.chk,
            self.btn,
            self.redir
        ]
        self.btn_go2a.register("click", self.on_go2a)
        self.btn.register("click", self.on_btn_click)

    def on_btn_click(self, source, message):
        print(f'Checked? {self.chk.checked}')
        self.chk.checked = True

    def on_go2a(self, source, message):
        self.redir.redirect('/a')


if __name__ == "__main__":
    mapp = MultiApp(
        a=ExampleAppA,
        b=ExampleAppB
    )
    mapp.run()
