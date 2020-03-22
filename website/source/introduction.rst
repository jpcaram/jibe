Introduction
============

Web applications require at least two pieces of software running
on a network: A client and a server. The server (known as the
back-end) is written in a variety of programming languages and
is under full control of developers. On the other hand, the
client (also known as the front end) runs in the user's browser
and is written almost exclusively in Javacript. This separation,
however convenient under some circumstances, is often
unnecessary, makes the development of a web application
very slow and error prone.

Jibe eliminates the need to write an independent client
application. It does this by generating everything that
needs to be shown
and run on the browser from the server side, transparently
and on-the-fly. Furthermore, when something is set on the
server, it is automatically updated on the browser, and
vise versa. As the user interacts with the browser, changes
are immediately reflected on the server.