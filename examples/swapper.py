import tornado.ioloop
from webpy import MainApp
from webpy import Widget, Button, Input, HBox, VBox, CheckBox, Label


class SwapperApp(MainApp):

    def __init__(self, connection):
        super().__init__(connection)

        self.button = Button("Swap", style={'margin': '3px'})
        self.secbox = HBox()
        st = {'width': '300px',
              'padding': '2px',
              'border': '1px solid gray',
              'margin': '3px'}
        self.left = VBox(style=st)
        self.right = VBox(style=st)

        self.secbox.children = [
            self.left, self.right
        ]

        self.labelA = Label("Label A")
        self.labelB = Label("label B")

        self.left.children = [self.labelA]
        self.right.children = [self.labelB]

        self.children = [
            self.button, self.secbox
        ]

        self.button.register('click', self.on_swap)

    def on_swap(self, source):

        left = self.left.children[0]
        right = self.right.children[0]

        self.left.children = [right]
        self.right.children = [left]


if __name__ == "__main__":
    # app = SwapperApp().make_app()
    app = SwapperApp.make_tornado_app()
    app.listen(8881)
    tornado.ioloop.IOLoop.current().start()