import tornado.ioloop
from webpy import MainApp
from webpy import Widget, Button, Input, HBox, VBox, CheckBox, Label


class TodoWidget(HBox):

    def __init__(self, label=""):
        super().__init__()

        self.checkbox = CheckBox()
        self.label = Label(label)
        self.children = [
            self.checkbox,
            self.label
        ]

    @property
    def completed(self):
        return self.checkbox.checked


class TodoListWidget(VBox):

    def __init__(self):
        super().__init__()

        self.entry = HBox()
        self.input = Input()
        self.entry.children = [
            self.input
        ]

        self.todolist = VBox()
        self.clear_button = Button("Clear Completed")

        self.children = [
            self.entry,
            self.todolist,
            self.clear_button
        ]

        # This form of attaching an event handler is for "secondary"
        # hanlers. Primary handlers are attached with @event_handler,
        # which are for events of its own widget. The primary handler
        # calls the secondary handlers. This is a secondary handler
        # beause it is an event of self.input, not self.
        self.input.register('change', self.on_add_todo)

        self.clear_button.register('click', self.on_clear_completed)

    def on_add_todo(self, source):
        new_todo = TodoWidget(self.input.value)
        self.todolist.children.append(new_todo)
        print(f"Added {repr(new_todo)}")

    def on_clear_completed(self, source):
        print(f'{self.__class__.__name__}.on_clear_completed({repr(source)}')

        for todo in self.todolist.children:
            if todo.completed:
                print(f'{todo.label._value} -- completed')
                self.todolist.children.remove(todo)


class ExampleApp(MainApp):

    def __init__(self):
        super().__init__()

        self.children = [
            TodoListWidget()
        ]


if __name__ == "__main__":
    # app = MainApp().make_app()
    app = ExampleApp().make_app()
    app.listen(8881)
    tornado.ioloop.IOLoop.current().start()
