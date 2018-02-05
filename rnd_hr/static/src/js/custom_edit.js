odoo.define('rnd_hr.custom_timeline', function (require) {
    "use strict";
    var form_widget = require('web.form_widgets');

   google.load("visualization", "1");

    var OrgChartButton = form_widget.WidgetButton.include({
        on_click: function () {

            if (this.node.attrs.custom === "click") {


                 // Set callback to run when API is loaded
                 google.setOnLoadCallback(this.drawVisualization());


            }else {
                this._super();
            }

        },

        drawVisualization: function () {
            var givendate = Date(2018, 0, 1);

            var data = [], timeline = undefined;
            var dataTbl = {
              "cols": [
                { "id": "", "label": "start", "pattern": "", "type": "datetime" },
                { "id": "", "label": "end", "pattern": "", "type": "datetime" },
                { "id": "", "label": "content", "pattern": "", "type": "string" },
                { "id": "", "label": "group", "pattern": "", "type": "string" },
                { "id": "", "label": "className", "pattern": "", "type": "string" }
              ],
              "rows": [
                {
                  "c": [
                    { "v": "Date(2018, 0, 31, 6, 36, 53, 743)" },
                    { "v": "Date(2018, 0, 31, 12, 36, 53, 743)" },
                    { "v": "Available" },
                    { "v": "Md.Abul Khair Titu [Driver]" },
                    { "v": "available" }
                  ]
                },
                {
                  "c": [
                    { "v": "Date(2018, 0, 31, 13, 36, 53, 743)" },
                    { "v": "Date(2018, 0, 31, 20, 36, 53, 743)" },
                    { "v": "Unavailable" },
                    { "v": "B" },
                    { "v": "unavailable" }
                  ]
                },
                {
                  "c": [
                    { "v": "Date(2018, 0, 31, 23, 36, 53, 743)" },
                    { "v": "Date(2018, 1, 1, 3, 36, 53, 743)" },
                    { "v": "Unavailable" },
                    { "v": "C" },
                    { "v": "unavailable" }
                  ]
                },
                {
                  "c": [
                    { "v": "Date(2018, 1, 1, 6, 36, 53, 743)" },
                    { "v": "Date(2018, 1, 1, 11, 36, 53, 743)" },
                    { "v": "Available" },
                    { "v": "D" },
                    { "v": "available" }
                  ]
                },
                {
                  "c": [
                    { "v": "Date(2018, 1, 1, 12, 36, 53, 743)" },
                    { "v": "Date(2018, 1, 1, 18, 36, 53, 743)" },
                    { "v": "Unavailable" },
                    { "v": "E" },
                    { "v": "unavailable" }
                  ]
                },
                {
                  "c": [
                    { "v": "Date(2018, 0, 31, 7, 36, 53, 747)" },
                    { "v": "Date(2018, 0, 31, 16, 36, 53, 747)" },
                    { "v": "Maybe" },
                    { "v": "F" },
                    { "v": "maybe" }
                  ]
                },
                {
                  "c": [
                    { "v": "Date(2018, 0, 31, 20, 36, 53, 747)" },
                    { "v": "Date(2018, 1, 1, 3, 36, 53, 747)" },
                    { "v": "Unavailable" },
                    { "v": "G" },
                    { "v": "unavailable" }
                  ]
                },
                {
                  "c": [
                    { "v": "Date(2018, 1, 1, 6, 36, 53, 747)" },
                    { "v": "Date(2018, 1, 1, 15, 36, 53, 747)" },
                    { "v": "Unavailable" },
                    { "v": "H" },
                    { "v": "unavailable" }
                  ]
                },
                {
                  "c": [
                    { "v": "Date(2018, 1, 1, 16, 36, 53, 747)" },
                    { "v": "Date(2018, 1, 1, 21, 36, 53, 747)" },
                    { "v": "Available" },
                    { "v": "I" },
                    { "v": "available" }
                  ]
                },
                {
                  "c": [
                    { "v": "Date(2018, 1, 1, 22, 36, 53, 747)" },
                    { "v": "Date(2018, 1, 2, 6, 36, 53, 747)" },
                    { "v": "Available" },
                    { "v": "J" },
                    { "v": "available" }
                  ]
                },
                {
                  "c": [
                    { "v": "Date(2018, 0, 31, 8, 36, 53, 748)" },
                    { "v": "Date(2018, 0, 31, 15, 36, 53, 748)" },
                    { "v": "Unavailable" },
                    { "v": "K" },
                    { "v": "unavailable" }
                  ]
                },
                {
                  "c": [
                    { "v": "Date(2018, 0, 31, 16, 36, 53, 748)" },
                    { "v": "Date(2018, 1, 1, 0, 36, 53, 748)" },
                    { "v": "Available" },
                    { "v": "L" },
                    { "v": "available" }
                  ]
                },
                {
                  "c": [
                    { "v": "Date(2018, 1, 1, 3, 36, 53, 748)" },
                    { "v": "Date(2018, 1, 1, 10, 36, 53, 748)" },
                    { "v": "Unavailable" },
                    { "v": "M" },
                    { "v": "unavailable" }
                  ]
                },
                {
                  "c": [
                    { "v": "Date(2018, 1, 1, 12, 36, 53, 748)" },
                    { "v": "Date(2018, 1, 1, 16, 36, 53, 748)" },
                    { "v": "Maybe" },
                    { "v": "N" },
                    { "v": "maybe" }
                  ]
                },
                {
                  "c": [
                    { "v": "Date(2018, 1, 1, 16, 36, 53, 748)" },
                    { "v": "Date(2018, 1, 1, 22, 36, 53, 748)" },
                    { "v": "Available" },
                    { "v": "O" },
                    { "v": "available" }
                  ]
                }
              ]
            };

            // Create and populate a data table.
            data = new google.visualization.DataTable(dataTbl);
            // data.addColumn('datetime', 'start');
            // data.addColumn('datetime', 'end');
            // data.addColumn('string', 'content');
            // data.addColumn('string', 'group');
            // data.addColumn('string', 'className');

            // create some random data
            // var names = ["Algie", "Barney", "Chris"];
            // for (var n = 0, len = names.length; n < len; n++) {
            //     var name = names[n];
            //     var now = new Date();
            //     var end = new Date(now.getTime() - 12 * 60 * 60 * 1000);
            //     for (var i = 0; i < 5; i++) {
            //         var start = new Date(end.getTime() + Math.round(Math.random() * 5) * 60 * 60 * 1000);
            //         var end = new Date(start.getTime() + Math.round(4 + Math.random() * 5) * 60 * 60 * 1000);
            //
            //         var r = Math.round(Math.random() * 2);
            //         var availability = (r === 0 ? "Unavailable" : (r === 1 ? "Available" : "Maybe"));
            //         var group = availability.toLowerCase();
            //         var content = availability;
            //         data.addRow([start, end, content, name, group]);
            //     }
            // }
            // debugger;

            // alert(data.toJSON());
            // specify options

            var options = {
                width:  "100%",
                height: "auto",
                layout: "box",
                axisOnTop: true,
                eventMargin: 3,  // minimal margin between events
                eventMarginAxis: 0, // minimal margin beteen events and the axis

                editable: false,
                showNavigation: true,
                zoomMin: 1000 * 60 * 60,
                zoomMax: 1000 * 60 * 60 * 24 * 365,
                showCurrentTime: true,
                showCustomTime: false,
                scale: 10
            };

            // Instantiate our timeline object.
            $('.o_form_sheet').html("");
            timeline = new links.Timeline($('.o_form_sheet'), options);

            // register event listeners
            google.visualization.events.addListener(timeline, 'edit', this.onEdit);

            // Draw our timeline with the created data and options
            timeline.draw(data);

            // Set a customized visible range
            var today = new Date();
            var date = new Date(2017, 5, 1);
            // var date = new Date(today.getFullYear(), today.getMonth(), 1);
            // var start = new Date(date.getTime() - 4 * 60 * 60 * 1000);
            var start = new Date(date.getTime());
            var end = new Date(date.getTime() + 20 * 24 * 60 * 60 * 1000);

            timeline.setVisibleChartRange(start, end);
        },

        getRandomName: function() {
            var names = ["Algie", "Barney", "Grant", "Mick", "Langdon"];

            var r = Math.round(Math.random() * (names.length - 1));
            return names[r];
        },

    getSelectedRow: function() {
        var row = undefined;
        var sel = timeline.getSelection();
        if (sel.length) {
            if (sel[0].row != undefined) {
                row = sel[0].row;
            }
        }
        return row;
    },

    strip: function(html)
    {
        var tmp = document.createElement("DIV");
        tmp.innerHTML = html;
        return tmp.textContent||tmp.innerText;
    },

    // Make a callback function for the select event
    onEdit: function (event) {
            alert("OnEdit");
        var row = this.getSelectedRow();
        var content = data.getValue(row, 2);
        var availability = this.strip(content);
        var newAvailability = prompt("Enter status\n\n" +
                "Choose from: Available, Unavailable, Maybe", availability);
        if (newAvailability != undefined) {
            var newContent = newAvailability;
            data.setValue(row, 2, newContent);
            data.setValue(row, 4, newAvailability.toLowerCase());
            timeline.draw(data);
        }
    },

    // var onNew = function () {
    //     alert("Clicking this NEW button should open a popup window where " +
    //             "a new status event can be created.\n\n" +
    //             "Apperently this is not yet implemented...");
    // };




    });
//
return {
    OrgChartButton: OrgChartButton
};

});