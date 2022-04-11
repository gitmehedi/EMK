odoo.define('pos_ticket.posticket',function(require){
"use strict"
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');


    var _orderline_super = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        get_service_charge: function(){
            return this.discount;
        },
        export_as_JSON: function(){
            var json = _orderline_super.export_as_JSON.apply(this, arguments);
            json.reward_id = this.reward_id;
            return json;
        },
        init_from_JSON: function(json){
            _orderline_super.init_from_JSON.apply(this, arguments);
            this.reward_id = json.reward_id;
        },
    });

    var _order_super = models.Order.prototype;
    models.Order = models.Order.extend({
        get_service_charge: function(){
            var charge = this.pos.config.service_charge;
            var service_charge = this.get_total_with_tax() * (charge / 100 );
            return service_charge;
        },
        finalize: function(){
            var client = this.get_client();
            _order_super.finalize.apply(this, arguments);
        },
        export_for_printing: function(){
            var json = _order_super.export_for_printing.apply(this, arguments);
            return json
        },
        export_as_JSON: function(){
            var json = _order_super.export_as_JSON.apply(this, arguments);
            return json;
        },

    });
    models.load_models([{
        model:'operating.unit',
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
    screens.OrderWidget.include({
        update_summary: function(){

            this._super();
            var order = this.pos.get_order();
            var charge = order ? order.get_service_charge() : 0;
            var total  = order ? order.get_total_with_tax() + charge : 0;

            this.el.querySelector('.summary .total .charge .value').textContent = this.format_currency(Math.round(charge));
        }
    });
});