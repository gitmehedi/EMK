from datetime import datetime
from odoo import api, fields, models
from odoo.tools.float_utils import float_compare
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_transfer(self):
        res = super(StockPicking, self).do_transfer()
        if res:
            picking = self.browse(self.ids)[0]
            indent_obj = self.env['indent.indent']
            indent_ids = indent_obj.search([('name', '=', picking.origin)])
            if indent_ids:
                picking_ids = self.search([('origin', '=', picking.origin)])
                flag = True
                # for picking in self.browse(self.ids):
                for picking in picking_ids:
                    if picking.state not in ('done', 'cancel'):
                        flag = False
                if flag:
                    indent_ids.write({'state': 'received'})

        return res