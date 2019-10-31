from jinja2 import Template, Environment, DictLoader

# html = """
# <!DOCTYPE html>
# <html>
# <head>
#     <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
#     <script src="app.js"></script>
#     <link rel="stylesheet" type="text/css" href="app.css">
# </head>
# <body>
#
#     <widget id="_topwidget">
#         <div class="widget" id="topwidget" style="display: flex; flex-direction: column;">
#         </div>
#         <script>
#         new Widget("topwidget", APP.wsopen);
#         </script>
#     </widget>
#
#     <script language="JavaScript">
#
#         APP.connect("ws://localhost:8881/websocket");
#
#         // var ws = new WebSocket("ws://localhost:8881/websocket");
#         // var wsopen = $.Deferred();
#         //
#         // ws.onopen = function() {
#         //     console.log("Websocket connection ready.");
#         //     wsopen.resolve();
#         // };
#         //
#         // ws.onmessage = function(evt) {
#         //     var messageDict = JSON.parse(evt.data);
#         //     console.log("Message received: ", messageDict);
#         //
#         //     // Message format:
#         //     // {id: ..., event: ..., ...}
#         //     // Widgets must implement $(...).on("message", function...)
#         //     $("#" + messageDict.id).trigger("message", messageDict);
#         // };
#         //
#         // //ws.send(JSON.stringify({msg: "Page started!"}));
#         //
#         // function message(msg) {
#         //     ws.send(JSON.stringify(msg));
#         // }
#         //
#         // var widgets = {};
#
#
#     </script>
# </body>
# </html>
# """

with open('../webpy/page.html') as f:
    html = f.read()
htmlt = Template(html)
