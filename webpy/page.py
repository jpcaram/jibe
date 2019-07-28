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
    <h1>The page</h1>
    
    {{body}}
    
    <script language="JavaScript">
        var ws = new WebSocket("ws://localhost:8888/websocket");
        
        ws.onmessage = function(evt) {
            var messageDict = JSON.parse(evt.data);
            console.log(messageDict);
        };
        
        //ws.send(JSON.stringify({msg: "Page started!"}));
        
        function message(msg) {
            ws.send(JSON.stringify(msg));
        }
    </script>
</body>
</html>
"""

# env = Environment()
htmlt = Template(html)