odoo.define('rnd_hr.custom_timeline', function (require) {

   "use strict";
   var form_widget = require('web.form_widgets');
   var ajax = require('web.ajax');
   // var Dialog = require('web.Dialog');
   var core = require('web.core');
   var _t = core._t;

   google.load("visualization", "1");

   var OrgChartButton = form_widget.WidgetButton.include({

        on_click: function () {

            if(this.node.attrs.custom === "click") {
                var self = this;
                this.onClick(self);

            }else {
                this._super();
            }

        },

        onClick: function(self){

            var operating_unit_id = self.field_manager.get_field_value('operating_unit_id');
            var department_id = self.field_manager.get_field_value('department_id');
            var employee_id = self.field_manager.get_field_value('employee_id');

            var params = {
                'operating_unit': operating_unit_id == false ?'':operating_unit_id,
                'department': department_id == false ?'-1':department_id,
                'employee': employee_id == false ? '-1': employee_id,
                'from_date': $('[name="from_date"]').val(),
                'to_date': $('[name="to_date"]').val(),
            };

            if (params['operating_unit'] && params['from_date'] && params['to_date']){
                ajax.jsonRpc("/employee/roster", 'call', {
                    'operating_unit_id': params['operating_unit'],
                    'department_id': params['department'],
                    'employee_id': params['employee'],
                    'from_date': params['from_date'],
                    'to_date': params['to_date']
                }).then(function (data) {
                    var dataList = $.parseJSON(data);
                    // Set callback to run when API is loaded
                    google.setOnLoadCallback(self.drawVisualization(params['from_date'], dataList));
                });
            }else{
                this.do_warn(_t("The following fields are invalid :"),'Please Select Input Field Correctly.');
                // this.do_warn(_t("Please Select Input Field Correctly"))
            }
        },

        drawVisualization: function (fromDate, dataList) {
            var dateArray = fromDate.split('/');
            var startDate = new Date(dateArray[2], dateArray[0] - 1, dateArray[1]);

            var data = [], timeline = undefined;

            // Create and populate a data table.
            data = new google.visualization.DataTable();
            data.addColumn('datetime', 'start');
            data.addColumn('datetime', 'end');
            data.addColumn('string', 'content');
            data.addColumn('string', 'group');
            data.addColumn('string', 'className');
            debugger;
            // Populate Data
            for (var n = 0, len = dataList.length; n < len; n++) {

                // "2018-02-01 17:00:00"
                var group = "available";
                var content = "Available";
                var obj = dataList[n];

                var name = obj.name;

                var type = obj.type;

                var startDutyTime = new Date(obj.startDutyTime);
                var endDutyTime = new Date(obj.endDutyTime);
                if (obj.dutyTime > 0){
                    group = "available";
                    content = obj.dutyTime.toString() + " Hrs";
                    data.addRow([startDutyTime, endDutyTime, content, name, group]);
                }


                if (obj.otDutyTime > 0){
                    var otStartDutyTime = new Date(obj.otStartDutyTime)
                    //var otStartDutyTime = new Date((new Date(obj.otStartDutyTime)).getTime() + 1000 * 60)
                    var otEndDutyTime = new Date(obj.otEndDutyTime);
                    group = "maybe";
                    content = obj.otDutyTime.toString() + " Hrs OT";
                    data.addRow([otStartDutyTime, otEndDutyTime, content, name, group]);
                }

            }

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
            // console.log(options);
            // console.log(timeline);
            // console.log(data);
            // debugger;
            timeline.draw(data);

            // Set a customized visible range
            var endDate = new Date(startDate.getTime() + 10 * 24 * 60 * 60 * 1000);

            timeline.setVisibleChartRange(startDate, endDate);
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