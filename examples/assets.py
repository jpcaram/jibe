from jibe import MainApp, HTML


class AppWithAssets(MainApp):

    assets_path = {'to': 'assets', 'from': 'data'}

    def __init__(self, connection):
        super().__init__(connection)

        self.children = [
            HTML("<img src='assets/image.png'/>")
        ]


if __name__ == "__main__":
    AppWithAssets.run(8881)
