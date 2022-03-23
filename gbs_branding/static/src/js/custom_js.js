odoo.define('gbs_branding.custom_js', function (require) {
    "use strict";

    var core = require('web.core'),
        data = require('web.data'),
        Dialog = require('web.Dialog'),
        Model = require('web.Model'),
        form_relational = require('web.form_relational'),
        _t  = core._t;


    var FieldMany2One = core.form_widget_registry.get('many2one');

//    FieldMany2One.include({
//         _search_create_popup: function(view, ids, context) {
////            var self = this;
////            alert('Working!')
//               this._search_create_popup("search", _data);
//        },
//    });

});
