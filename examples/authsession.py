from webpy import MainApp, Button, Input, CheckBox, WebSocketHandler, \
    Redirect, Label, VBox, HBox
import tornado.web
import tornado.ioloop
from pathlib import Path


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

    def on_click(self, source):
        self.status.value = ''

        if self.pwinput.value == "password":
            sid = self.connection.get_cookie('sessionid')
            self.connection.application.sessions[sid] = {
                'authenticated': True
            }
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
    cookie must exist as well.
    """

    def __init__(self, connection):

        # Widget.__init__: A lot of stuff.
        # MainApp.__init__: self.connection = connection
        super().__init__(connection)

        sid = connection.get_cookie('sessionid')
        session = connection.application.get_session(sid)
        print(f'[{__class__.__name__}] Session: {session}')
        if not session:
            self.children = [Label('Not authorized')]  # Will never happen
            connection.close()
            return

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

    def on_inbox_change(self):
        print(f'{self.__class__.__name__}.on_inbox_change()')

    def on_button_click(self, source):
        print(f'{self.__class__.__name__}.on_button_click()')
        self.inbox.value = f"{self.connection.get_cookie('sessionid')}"

    def on_logout(self, source):
        sid = self.connection.get_cookie('sessionid')
        del self.connection.application.sessions[sid]
        self.redir.redirect('/a')


class WSHA(WebSocketHandler):
    mainApp = AuthenticationApp


class WSHB(WebSocketHandler):
    mainApp = ExampleApp


from webpy import htmlt
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


class MultiApp(tornado.web.Application):

    def __init__(self):

        self.sessions = {}

        super().__init__([
            (r"/(a|b)", MainHandler_),
            (r"/a/websocket", WSHA),
            (r"/b/websocket", WSHB),
            (r"/(.*\.js)", tornado.web.StaticFileHandler, {"path": f"{Path(__file__).parent.absolute()}/../webpy/"}),
            (r"/(.*\.css)", tornado.web.StaticFileHandler, {"path": f"{Path(__file__).parent.absolute()}/../webpy/"})
        ])

    def get_session(self, sid):

        try:
            return self.sessions[sid]
        except KeyError:
            return None


if __name__ == "__main__":
    MultiApp().listen(8881)
    tornado.ioloop.IOLoop.current().start()
