from jinja2 import Template, Environment, DictLoader

html = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
    <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">
    <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
</head>
<body>
    
    {{body}}
    
    <script language="JavaScript">
        $( document ).on("wsconnected", function() {
            console.log("Websocket connection ready.");
        });
        var ws = new WebSocket("ws://localhost:8881/websocket");
        ws.onopen = function() {
            $( document ).trigger("wsconnected");
        };
        
        ws.onmessage = function(evt) {
            var messageDict = JSON.parse(evt.data);
            console.log("Message received: ", messageDict);
            
            // Message format:
            // {id: ..., event: ..., ...}
            // Widgets must implement $(...).on("message", function...)
            $("#" + messageDict.id).trigger("message", messageDict);
        };
        
        //ws.send(JSON.stringify({msg: "Page started!"}));
        
        function message(msg) {
            ws.send(JSON.stringify(msg));
        }
        
        var widgets = {};
        
        
    </script>
</body>
</html>
"""

# env = Environment()
htmlt = Template(html)