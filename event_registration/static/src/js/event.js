odoo.define('event_registration.event', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var Widget = require('web.Widget');
    var web_editor_base = require('web_editor.base')

    var event = require('website_event.website_event');
    var websiteEvent = event.EventRegistrationForm;

    event.EventRegistrationForm.include({
        start: function () {
            var self = this;
            $('#registration_form .a-submit').off('click').click(function (ev) {
                    self.on_click(ev);
                });
            return self;
        },
        on_click: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var $form = $(ev.currentTarget).closest('form');
            var post = {};
            $("#registration_form select").each(function () {
                post[$(this).attr('name')] = 1;
            });
            return ajax.jsonRpc($form.attr('action'), 'call', post).then(function (modal) {
                var $modal = $(modal);
                $modal.find('.modal-body > div').removeClass('container'); // retrocompatibility - REMOVE ME in master / saas-19
                $modal.modal('show');
                $modal.on('click', '.js_goto_event', function () {
                    $modal.modal('hide');
                });
            });
        },

    });

});


