from webpy import MainApp, Button, Input


class ExampleApp(MainApp):

    # def __new__(cls, connection):
    #     instance = super(ExampleApp, cls).__new__(cls)
    #     super(ExampleApp, cls).__init__(instance, connection)
    #     return instance

    def __init__(self, connection):
        super().__init__(connection)
        self.children = [
            Button(),
            Input(value='The value')
        ]
        self.children[0].register('click', self.on_button_click)

    def on_button_click(self, source):
        self.children[1].value = "Hello!"


if __name__ == "__main__":
    ExampleApp.run(port=8881)
