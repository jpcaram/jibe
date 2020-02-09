import tornado.ioloop
from webpy import MainApp
from webpy import CheckBox, Button


class ExampleApp(MainApp):

    def __init__(self, connection):
        super().__init__(connection)

        self.chk = CheckBox()
        self.btn = Button()

        self.children = [
            self.chk,
            self.btn
        ]

        self.btn.register("click", self.on_btn_click)

    def on_btn_click(self, event):
        print(f'Checked? {self.chk.checked}')
        self.chk.checked = True


if __name__ == "__main__":
    ExampleApp.run(8881)
