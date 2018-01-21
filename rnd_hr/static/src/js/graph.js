odoo.define('rnd_hr.custom', function (require) {
    "use strict";
    var form_widget = require('web.form_widgets');


    var OrgChartButton = form_widget.WidgetButton.include({
        on_click: function () {
            var self = this;
            self._super();
            // google2 = new google();
            alert('1 alert')
            // if (this.node.attrs.custom === "click") {
            alert('2 alert')
            google.load("visualization", "1");
            alert('3 alert')
            google.setOnLoadCallback(self.drawVisualization);
            alert('4 alert')
            // }
        },
        drawVisualization: function () {
            // Create and populate a data table.
            var data = new google.visualization.DataTable();
            data.addColumn('datetime', 'time');
            data.addColumn('number', 'Function A');
            data.addColumn('number', 'Function B');

            function functionA(x) {
                return Math.sin(x / 25) * Math.cos(x / 25) * 50 + (Math.random() - 0.5) * 10;
            }

            function functionB(x) {
                return Math.sin(x / 50) * 50 + Math.cos(x / 7) * 75 + (Math.random() - 0.5) * 20 + 20;
            }

            // create data
            var d = new Date(2010, 9, 23, 20, 0, 0);
            for (var i = 0; i < 100; i++) {
                data.addRow([new Date(d), functionA(i), functionB(i)]);
                d.setMinutes(d.getMinutes() + 1);
            }

            // specify options
            var options = {
                "width": "100%",
                "height": "350px"
            };

            // Instantiate our graph object.
            var graph = new links.Graph(document.getElementById('mygraph'));

            // Draw our graph with the created data and options
            graph.draw(data, options);
        }


    });

    return {
        OrgChartButton: OrgChartButton
    };

});