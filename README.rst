The Jibe Full-Stack Framework
=============================

Website: `<http://jibe.caram.cl/>`_ - Repository: `https://github.com/jpcaram/jibe`_

Jibe is a Full-Stack Library and Framework for developing
highly interactive web applications in pure Python.

It focuses on clean, resusable, understandable, object-oriented
code, and on security and quick prototyping. Developers can create
full-stack applications very quickly without
sacrificing security and maintainability.

Here is an example application:

.. code-block:: python

    from jibe import MainApp, Button, Input

    class ExampleApp(MainApp):

       def __init__(self, connection):
           super().__init__(connection)
           self.children = [
               Button(),
               Input(value='The value')
           ]
           self.children[0].register('click', self.on_button_click)

       def on_button_click(self, source, message):
           self.children[1].value = "Hello!"

    if __name__ == "__main__":
       ExampleApp.run(port=8881)

