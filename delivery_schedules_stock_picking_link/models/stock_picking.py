from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_new_transfer(self):
        if self.picking_type_id.code == 'outgoing':
            # get active model
            active_model = self.env.context.get('active_model', False)
            if active_model != 'delivery.schedules.line':
                raise UserError(_("You cannot validate a DC which is not coming via delivery schedules."))

        return super(StockPicking, self).do_new_transfer()

    @api.multi
    def do_transfer(self):
        # do default operation
        res = super(StockPicking, self).do_transfer()

        if self.picking_type_id.code == 'outgoing':
            # get active model
            active_model = self.env.context.get('active_model', False)
            # check whether active model is 'delivery.schedules.line' or not
            # if condition is true, the following code will execute
            if active_model == 'delivery.schedules.line':
                active_id = self.env.context.get('active_id')
                delivery_schedules_line = self.env[active_model].browse(active_id)

                # delivery order line
                line = self.delivery_order_id.line_ids[0]

                # update delivery schedules line
                delivery_schedules_line.write({
                    'ordered_qty': line.quantity,
                    'undelivered_qty': line.quantity - line.qty_delivered,
                    'state': 'done'
                })

        return res
