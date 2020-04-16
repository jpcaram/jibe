# Jibe
# A Full-Stack Pure-Python Web Framework.
# Copyright (c) 2020 Juan Pablo Caram
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from jibe import MainApp, MainHandler, \
    WebSocketHandler, Label, VBox
import tornado.web
import tornado.ioloop
from pathlib import Path


class GooglePieChart(VBox):
    """
    TODO: This example needs updating.
    """

    def __init__(self):
        super().__init__()

        self._jsrender = f"""
        gchartprom.done(function() {{
            console.log("Attempting to render the chart!");
        
            // Create the data table.
            var data = new google.visualization.DataTable();
            data.addColumn('string', 'Topping');
            data.addColumn('number', 'Slices');
            data.addRows([
              ['Mushrooms', 3],
              ['Onions', 1],
              ['Olives', 1],
              ['Zucchini', 1],
              ['Pepperoni', 2]
            ]);
    
            // Set chart options
            var options = {{'title':'How Much Pizza I Ate Last Night',
                           'width':400,
                           'height':300}};
    
            // Instantiate and draw our chart, passing in some options.
            var chart = new google.visualization.PieChart(
               //document.getElementById('{self.identifier}')
               this.el
            );
            chart.draw(data, options);
        
        }}.bind(this));
        """


class ExampleApp(MainApp):

    def __init__(self, connection):
        super().__init__(connection)

        self.children = [
            Label('3rd Party Widget'),
            GooglePieChart()
        ]


class MainHandlerTP(MainHandler):

    def scripts(self):
        return ["https://www.gstatic.com/charts/loader.js"]

    def presetup(self):
        return """
        let gchartprom = $.Deferred();
        google.charts.load('current', {'packages':['corechart']});
        function resolvegchart() { gchartprom.resolve(); } 
        google.charts.setOnLoadCallback(resolvegchart);
        """


class WSH(WebSocketHandler):
    mainApp = ExampleApp


class MultiApp(tornado.web.Application):

    def __init__(self):

        super().__init__([
            (r"/", MainHandlerTP),
            (r"/websocket", WSH),
            (r"/(.*\.js)", tornado.web.StaticFileHandler, {"path": f"{Path(__file__).parent.absolute()}/../webpy/"}),
            (r"/(.*\.css)", tornado.web.StaticFileHandler, {"path": f"{Path(__file__).parent.absolute()}/../webpy/"})
        ])


if __name__ == "__main__":
    MultiApp().listen(8881)
    tornado.ioloop.IOLoop.current().start()
