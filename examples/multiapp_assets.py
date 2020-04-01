# Jibe
# A Full-Stack Pure-Python Web Framework.
# Copyright (c) 2020 Juan Pablo Caram
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from jibe import MainApp, Button, Input, CheckBox, \
    Redirect, MultiApp, HTML
from pathlib import Path


class ExampleAppA(MainApp):

    assets_path = {
        'to': 'assets',
        'from': f'{Path(__file__).parent.absolute()}/data'
    }

    def __init__(self, connection):
        super().__init__(connection)

        self.btn_go2b = Button(label='Go to B')
        self.redir = Redirect()

        self.children = [
            self.btn_go2b,
            HTML('<img src="/a/assets/image_orange.png"/>'),
            HTML('<img src="/image.png"/>'),
            self.redir
        ]

        self.btn_go2b.register("click", self.on_go2b)

    def on_go2b(self, source, message):
        self.redir.redirect('/b')


class ExampleAppB(MainApp):
    assets_path = {
        'to': 'assets',
        'from': f'{Path(__file__).parent.absolute()}/data'
    }

    def __init__(self, connection):
        super().__init__(connection)

        self.btn_go2a = Button(label='Go to A')
        self.redir = Redirect()

        self.children = [
            self.btn_go2a,
            HTML('<img src="/b/assets/image_blue.png"/>'),
            HTML('<img src="/image.png"/>'),
            self.redir
        ]

        self.btn_go2a.register("click", self.on_go2a)

    def on_go2a(self, source, message):
        self.redir.redirect('/a')


mapp = MultiApp(
    a=ExampleAppA,
    b=ExampleAppB,
    assets_path={
        'to': '',
        'from': f'{Path(__file__).parent.absolute()}/data'
    }
)

if __name__ == "__main__":

    mapp.run()
