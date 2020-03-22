.. webpy documentation master file, created by
   sphinx-quickstart on Sat Feb  8 11:59:53 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

The Jibe Full-Stack Framework
=============================

Jibe is a Full-Stack Library and Framework for developing
highly interactive web applications in pure Python.

It focuses on clean, resusable, understandable, object-oriented
code, and on security and quick prototyping. Developers can create
full-stack applications very quickly without
sacrificing security and maintainability.

Even though Jibe comes with many predefined defaults that in
general make sense, it does not impose any coding style or
structure, neither a visual appearance or behavior of your
front-end. Everything is highly customizable.

.. note:: Jibe is under active development at this time. Its
   API and behavior are expected to change. If you plan to use
   Jibe for your target application today, please see the
   :ref:`roadmap`.

.. _example1:

Here is an example application (**example #1**)::

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


And in the browser:

.. image:: basic.png

When you click on the button, the text in the input box changes to
"Hello!".


Contents
========

.. toctree::
   :maxdepth: 2

   introduction
   tutorial1
   corewidgets
   examples
   widgets
   widgetapi
   appapi
   roadmap


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
