odoo.define('appointments.main', function (require) {
    'use strict';

    var core = require('web.core');
    var ajax = require('web.ajax');
    var publicWidget = require('web_editor.snippets.animation');
    var _t = core._t;
    var active_day=[];
    var weekday = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];

    publicWidget.registry.Appointments = publicWidget.Class.extend({
        selector: '#appointment_reservation',
        init: function () {
            this._super.apply(this, arguments);
        },
        start: function () {
            var self = this;
            $('#appointment-reservation').validator();
            $("#appointment_date").datepicker({
                minDate: '+1D',
                maxDate: new Date(2050,12,31),
                changeMonth: true,
                changeYear: true,
                dateFormat: 'yy-mm-dd',
                beforeShowDay: _nonScheduleDate
            });

            $("#date").datepicker({
                minDate: '+1D',
                maxDate: new Date(2050,12,31),
                changeMonth: true,
                changeYear: true,
                dateFormat: 'yy-mm-dd',
            });

            function _nonScheduleDate(date){
                var day_of_week = date.getDay();
                if ( active_day.indexOf(day_of_week) !== -1){
                    return [true];
                }
                return [false];
            }

            $("#topic_id").on('change', function() {
                var topic_id =  $(this).find(":selected").val();
                if (topic_id !='' ){
                    var data = {
                        "topic_id": topic_id
                    }
                    self._update_contacts(data);
                }
            });
            $("#phone").on('change', function() {
                var phone =  $(this).val();
                if (phone){
                    self._valid_phone_number(phone);
                }
            });
            $("#contact_id").on("change",function(){
                var contact_id =  $("#contact_id").find(":selected").val();
                if ( contact_id !=''){
                    var data = {
                        "contact_id": contact_id,
                    }
                    self._update_date(data);
                }
                $("#appointment_date").val('');
                $("#timeslot_id").val('');
            });
            $("#appointment_date").on("change",function(){
                var contact_id =  $("#contact_id").find(":selected").val();
                var appointment_date =  $("#appointment_date").val();
                if ( contact_id !='' &&  appointment_date !=''){
                    var data = {
                        "contact_id": contact_id,
                        "appointment_date": appointment_date,
                    }
                    self._update_time_slot(data);
                }
                $("#timeslot_id").val('');
            });
            $("#glcm-matrix td").on("click",function(){
                var value = $(this).text().trim();
                $("#seat_no").text(value);
                $("input#seat_no_input").val(value);
            });
        },
        _format_date: function (date) {
            var self = this;

            var d = new Date(date),
                month = '' + (d.getMonth() + 1),
                day = '' + d.getDate(),
                year = d.getFullYear();

            if (month.length < 2)
                month = '0' + month;
            if (day.length < 2)
                day = '0' + day;

            return [year, month, day].join('-');
        },
        _update_contacts: function(data){
            var self = this;
            ajax.jsonRpc('/appointment/contacts','call',data).always(function(res){
                var contact_ids = res.contacts;
                var options = [];
                options.push('<option value="">--Please Select--</option>');
                for (var i=0; i < contact_ids.length ; i++ ){
                    options.push('<option value="' + contact_ids[i].id +'">' + contact_ids[i].name + '</option>');
                }
                $('#contact_id').html(options.join(''));
            });
        },
        _update_time_slot: function(data){
            var self = this;
            ajax.jsonRpc('/appointment/available-slot','call', data).always(function(res){
                var slots = res.slots;
                var options=[];
                options.push('<option value="">--Please Select--</option>');
                for (var i = 0; i < slots.length ; i++ ){
                    options.push('<option value="' + slots[i].id +'">' + slots[i].name + '</option>');
                }
                $('#timeslot_id').html(options.join(''));

            });
        },
        _update_date: function(data){
            var self = this;
            ajax.jsonRpc('/appointment/available-date','call', data).always(function(res){
                var days = res.days;
                var tags=[];
                active_day=[];
                for(var i=0;i<days.length;i++){
                    var r=Math.floor(Math.random()*255)
                    var g=Math.floor(Math.random()*255)
                    var b=Math.floor(Math.random()*255)
                    var color = 'rgb('+r+','+g+','+b+')';
                    var index = weekday.indexOf(days[i]);
                    if ( index !== -1){
                        active_day.push(index);
                        tags.push('<span style="background-color:'+ color +'">' + days[i] + '</span>');
                    }
                }
                $('#weekday_days').html(tags.join(''));
            });
        },
        _valid_phone_number: function (phone){
          var phonePattern = /^(880)([0-9]{10})$/;

          if (phone.match(phonePattern))
          {
              return true;
          } else {
              return false;
          }
        },
        _update_timeslot: function () {
            var self = this;

            ajax.jsonRpc('/appointment/available-slot', 'call', {
                'appointment_option': $("#appointment_option_id").val(),
                'appointment_with': $("#appointee_id").val(),
                'appointment_date': $("#appointment_date").val(),
                'form_criteria': $("#form_criteria").val(),
            }).always(function (result) {
                self.focus_year = result.focus_year;
                self.focus_month = result.focus_month;
                self.days_with_free_slots[self._get_yearmonth_key.bind(self)()] = result.days_with_free_slots;
                var options = [];
                var timeslots = result.timeslots;
                options.push('<option value="">-:--</option>');
                for (var i = 0; i < timeslots.length; i++) {
                    options.push('<option value="', timeslots[i].id, '">', timeslots[i].timeslot, '</option>')
                }
                $("#timeslot_id").html(options.join(''));

                var options = [];
                var appointees = result.appointees;
                options.push('<option value="">Select</option>');
                for (var i = 0; i < appointees.length; i++) {
                    if (appointees[i].id === result.appointment_with) {
                        options.push('<option value="', appointees[i].id, '" selected="True">', appointees[i].name, '</option>')
                    } else {
                        options.push('<option value="', appointees[i].id, '">', appointees[i].name, '</option>')
                    }
                }
                $("#appointee_id").html(options.join(''));
            });
        },
        _update_days_with_free_slots: function (year, month) {
            var self = this;

            ajax.jsonRpc('/online-appointment/month-bookable', 'call', {
                'appointment_option': $("#appointment_option_id").val(),
                'appointment_with': $("#appointee_id").val(),
                'appointment_year': year,
                'appointment_month': month,
                'form_criteria': $("#form_criteria").val(),
            }).always(function (result) {
                self.focus_year = result.focus_year;
                self.focus_month = result.focus_month;
                self.days_with_free_slots[self._get_yearmonth_key.bind(self)()] = result.days_with_free_slots;
                $(".datepicker" ).datepicker("refresh");
            });
        },
        _get_yearmonth_key: function() {
            var key = this.focus_year.toString() + ',' + this.focus_month.toString();
            return key
        },
    }),

    publicWidget.registry.AppointmentPortal = publicWidget.Class.extend({
        selector: '#online_appointment_interaction',
        start: function () {
            var self = this;
            var button_cancel = $('#cancel_appointment_button');
            var button_confirm = $('#confirm_appointment_button');

            button_cancel.click(function() {
                var dialog = $('#cancel_appointment_dialog').modal('show');
            });

            button_confirm.click(function() {
                var dialog = $('#confirm_appointment_dialog').modal('show');
            });
        }
    })
});
