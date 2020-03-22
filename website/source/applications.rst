Applications
============

This section of the documentation covers what there is beyond
a top-level ``Widget` in an application. Example #1 shows an application
created by subclassing MainApp, which is a Widget. To start
a server with just this application, we call its ``run()``
method. However, a full web application may require additional
assets like images, Javascript files, CSS, and often
multiple applications need to be served together.

Jibe applications (one or more) are served by the Tornado
web server. 

