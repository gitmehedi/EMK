odoo.define('rnd_hr.custom_timeline', function (require) {
    "use strict";
    var form_widget = require('web.form_widgets');

    var OrgChartButton = form_widget.WidgetButton.include({
        on_click: function () {

            if (this.node.attrs.custom === "click") {
                // google.load("visualization", "1");

                // // Set callback to run when API is loaded
                this.drawVisualization();

            }else {
                this._super();
            }

        },

        drawVisualization: function () {

            // Create and populate a data table.
            // data = new google.visualization.DataTable();
            // data.addColumn('datetime', 'start');
            // data.addColumn('datetime', 'end');
            // data.addColumn('string', 'content');
            // data.addColumn('string', 'group');
            // data.addColumn('string', 'className');

            var data = [], timeline = undefined;

        // create some random data
        var names = ["Algie", "Barney", "Chris"];
        for (var n = 0, len = names.length; n < len; n++) {
            var name = names[n];
            var now = new Date();
            var end = new Date(now.getTime() - 12 * 60 * 60 * 1000);
            for (var i = 0; i < 5; i++) {
                var start = new Date(end.getTime() + Math.round(Math.random() * 5) * 60 * 60 * 1000);
                var end = new Date(start.getTime() + Math.round(4 + Math.random() * 5) * 60 * 60 * 1000);

                var r = Math.round(Math.random() * 2);
                var availability = (r === 0 ? "Unavailable" : (r === 1 ? "Available" : "Maybe"));
                var group = availability.toLowerCase();
                var content = availability;
                data.push([start, end, content, name, group]);
            }
        }

        // specify options
        var options = {
            width:  "100%",
            height: "99%",
            layout: "box",
            axisOnTop: true,
            eventMargin: 10,  // minimal margin between events
            eventMarginAxis: 0, // minimal margin beteen events and the axis
            editable: true,
            showNavigation: true
        };

        // Instantiate our timeline object.
        $('.o_form_sheet').html("");
        timeline = new links.Timeline($('.o_form_sheet'), options);

        // register event listeners
        //google.visualization.events.addListener(timeline, 'edit', this.onEdit);

        // Draw our timeline with the created data and options
        timeline.draw(data);

        // Set a customized visible range
        var start = new Date(now.getTime() - 4 * 60 * 60 * 1000);
        var end = new Date(now.getTime() + 8 * 60 * 60 * 1000);
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