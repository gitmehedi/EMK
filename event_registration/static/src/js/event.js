odoo.define('event_registration.eventdfd', function (require) {
"use strict";

    var ajax = require('web.ajax');
    var Widget = require('web.Widget');
    var web_editor_base = require('web_editor.base')

    var event= require('website_event.website_event');
    var websiteEvent= event.EventRegistrationForm;

    websiteEvent.include({
        start: function() {
        var self = this;
        var res = this._super.apply(this,arguments).then(function() {
            $('#registration_form .a-submit')
                .off('click')
                .removeClass('a-submit')
                .click(function (ev) {
                    $(this).attr('disabled', true);
                    self.on_click(ev);
                });
        });
        return res
    },
    on_click: function(ev) {
        ev.preventDefault();
        ev.stopPropagation();
        var $form = $(ev.currentTarget).closest('form');
        var post = {};
        $("#registration_form select").each(function() {
            post[$(this).attr('name')] = 1;
        });
        return ajax.jsonRpc($form.attr('action'), 'call', post).then(function (modal) {
            var $modal = $(modal);
            $modal.find('.modal-body > div').removeClass('container'); // retrocompatibility - REMOVE ME in master / saas-19
            $modal.after($form).modal();
            $modal.on('click', '.js_goto_event', function () {
                $modal.modal('hide');
            });
        });
    },

    });

});


