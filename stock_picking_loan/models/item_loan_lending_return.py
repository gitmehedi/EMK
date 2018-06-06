from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class LoanLending(models.Model):
    _inherit = 'item.loan.lending'

    @api.multi
    def action_view_picking(self):
        picking_type_objs = self.env['stock.picking.type'].search(
            [('warehouse_id.operating_unit_id', '=', self.env.user.default_operating_unit_id.id),
             ('code', '=', 'incoming')])
        location_id = self.env['stock.location'].search([('usage', '=', 'supplier')], limit=1).id

        res = self.env.ref('stock_picking_extend.view_stock_picking_form1')

        result = {
            'name': _('Stock'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'context': {'default_picking_type_id': picking_type_objs[0].id,
                        'default_location_id' : location_id,
                        'default_transfer_type': 'receive',
                        'default_receive_type': 'loan',
                        'default_loan_id': self.id,
                        },
        }

        return result
