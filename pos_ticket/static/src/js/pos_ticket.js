odoo.define('pos_ticket.posticket', function (require) {
    "use strict"
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');

    models.load_models([{
        model: 'operating.unit',
        fields: [],
        domain: function (self) {
            return [['id', '=', self.config.operating_unit_id[0]]];
        },
        loaded: function (self, unit) {
            self.unit = unit[0];
            self.partner = []
            for (var i = 0; i < unit[0].length; i++) {
                if (unit[i].id === self.company.country_id[0]) {
                    self.company.country = self.unit.partner_id;
                }
            }
        },
    }]);
});