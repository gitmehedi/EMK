from odoo import api, fields, models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_transfer(self):
        res = super(StockPicking, self).do_transfer()
        if res:
            picking = self.browse(self.ids)[0]
            self.pack_operation_ids.filtered(lambda o: o.qty_done >= 0)


        return res