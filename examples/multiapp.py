from webpy import MainApp, Button, Input, CheckBox, WebSocketHandler, \
    Redirect
import tornado.web
from pathlib import Path


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

    def on_button_click(self, source):
        self.input.value = "Hello!"

    def on_go2b(self, event):
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

    def on_btn_click(self, event):
        print(f'Checked? {self.chk.checked}')
        self.chk.checked = True

    def on_go2a(self, event):
        self.redir.redirect('/a')


class WSHA(WebSocketHandler):
    mainApp = ExampleAppA


class WSHB(WebSocketHandler):
    mainApp = ExampleAppB


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


app = tornado.web.Application(
    [
        (r"/(a|b)", MainHandler_),
        (r"/a/websocket", WSHA),
        (r"/b/websocket", WSHB),
        (r"/(.*\.js)", tornado.web.StaticFileHandler, {"path": f"{Path(__file__).parent.absolute()}/../webpy/"}),
        (r"/(.*\.css)", tornado.web.StaticFileHandler, {"path": f"{Path(__file__).parent.absolute()}/../webpy/"})
    ]
)

if __name__ == "__main__":
    app.listen(8881)
    tornado.ioloop.IOLoop.current().start()