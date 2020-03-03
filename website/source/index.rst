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


.. _example1:

Here is an example application (**example #1**)::

   from webpy import MainApp, Button, Input

   class ExampleApp(MainApp):

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


And in the browser:

.. image:: basic.png

When you click on the button, the text in the input box changes to
"Hello!".

Introduction
============

Web applications require at least two pieces of software running
on a network: A client and a server. The server (known as the
back-end) is written in a variety of programming languages and
is under full control of developers. On the other hand, the
client (also known as the front end) runs in the user's browser
and is written almost exclusively in Javacript. This separation,
however conveninent under some circumstances, is often
unnecessary, making the development of a web application
very slow and error prone.

Jibe eliminates the need to write an independent client
application. It does this by generating everything that
needs to be shown
and run on the browser from the server side, transparently
and on-the-fly. Furthermore, when something is set on the
server, it is automatically updated on the browser, and
vise versa. As the user interacts with the browser, changes
are immediately reflected on the server.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   tutorial1
   widgets


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
