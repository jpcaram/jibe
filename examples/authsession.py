# Jibe
# A Full-Stack Pure-Python Web Framework.
# Copyright (c) 2020 Juan Pablo Caram
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from jibe import MainApp, Button, Input, CheckBox, WebSocketHandler, \
    Redirect, Label, VBox, HBox
import tornado.web
import tornado.ioloop
from pathlib import Path


class Session:

    def __init__(self):

        self.authenticated = False


class AuthenticationApp(MainApp):

    def __init__(self, connection):
        super().__init__(connection)

        self.label = Label('Password')
        self.pwinput = Input()
        self.btn = Button('Login')

        # TODO: If not a child, should raise error when calling redirect().
        self.redir = Redirect()
        self.status = Label('Please enter your password.')

        lg = HBox()
        lg.children = [
            self.label,
            self.pwinput,
            self.btn,
            self.redir
        ]

        vb = VBox()
        vb.children = [
            lg,
            self.status
        ]

        self.children = [
            vb
        ]

        self.btn.register("click", self.on_click)

        # ---- Authentication Verification ----
        # If authenticated, redirect immediately to the
        # main (restricted app).
        sid = connection.get_cookie('sessionid')
        session = connection.application.get_session(sid)
        print(f'[{__class__.__name__}] Session: {session}')
        if session.authenticated:
            self.redir.redirect('/b')
        # -------------------------------------

    def on_click(self, source, message):
        self.status.value = ''

        if self.pwinput.value == "password":
            sid = self.connection.get_cookie('sessionid')
            session = self.connection.application.get_session(sid)
            session.authenticated = True
            self.redir.redirect('/b')
            self.status.value = 'Success'  # This works???
        else:
            self.status.value = "Incorrect password. Try again."


class ExampleApp(MainApp):
    """
    The cookie 'sessionid' is checked and created if non-existent
    by MainHandler.get(), which is invoked when the body of the page
    is requested. I think it is not possible to set cookies via
    websockets and that is why it is done that way.

    At the time an instance of the MainApp exists, the 'sessionid'
    cookie does exist as well.
    """

    def __init__(self, connection):

        # Widget.__init__: A lot of stuff.
        # MainApp.__init__: self.connection = connection
        super().__init__(connection)

        # #### Authentication Verification #####
        sid = connection.get_cookie('sessionid')
        session = connection.application.get_session(sid)
        print(f'[{__class__.__name__}] Session: {session}')
        if not session.authenticated:
            self.children = [Label('Not authorized')]  # Will never happen
            connection.close()
            return
        # ### Done with authentication verification ####

        self.button = Button()
        self.inbox = Input()

        self.box1 = HBox()
        self.box1.children = [
            self.button,
            self.inbox
        ]

        self.logoutbtn = Button('Log out')

        self.box2 = VBox()
        self.box2.children = [
            Label("This the main app. You have been successfully authenticated."),
            self.box1,
            self.logoutbtn
        ]

        self.redir = Redirect()
        self.children = [self.box2, self.redir]

        self.button.register('click', self.on_button_click)
        self.logoutbtn.register('click', self.on_logout)

    # def on_inbox_change(self):
    #     print(f'{self.__class__.__name__}.on_inbox_change()')

    def on_button_click(self, source, message):
        # print(f'{self.__class__.__name__}.on_button_click()')
        self.inbox.value = f"{self.connection.get_cookie('sessionid')}"

    def on_logout(self, source, message):
        sid = self.connection.get_cookie('sessionid')
        del self.connection.application.sessions[sid]
        self.redir.redirect('/a')


class WSHA(WebSocketHandler):
    mainApp = AuthenticationApp


class WSHB(WebSocketHandler):
    mainApp = ExampleApp


from jibe import htmlt
from random import choice
letter = 'abcdefghijklmnopqrstuvwxyz1234567890'


# noinspection PyAbstractClass
class MainHandler_(tornado.web.RequestHandler):
    """
    Serves the top level html and core elements (javascript) of
    the application.
    """

    def get(self, appname):

        sessionid = self.get_cookie("sessionid")
        if not sessionid:
            sessionid = ''.join(choice(letter) for _ in range(10))
            self.set_cookie("sessionid", sessionid)

        self.write(htmlt.render({
            'appname': appname
        }))


folder = 'jibe'


class MultiApp(tornado.web.Application):

    def __init__(self):

        self.sessions = {}

        super().__init__([
            (r"/(a|b)", MainHandler_),
            (r"/a/websocket", WSHA),
            (r"/b/websocket", WSHB),
            (r"/(.*\.js)", tornado.web.StaticFileHandler, {"path": f"{Path(__file__).parent.absolute()}/../{folder}/"}),
            (r"/(.*\.css)", tornado.web.StaticFileHandler, {"path": f"{Path(__file__).parent.absolute()}/../{folder}/"})
        ])

    def get_session(self, sid):

        try:
            return self.sessions[sid]
        except KeyError:
            session = Session()
            self.sessions[sid] = session
            return session


if __name__ == "__main__":
    MultiApp().listen(8881)
    tornado.ioloop.IOLoop.current().start()
