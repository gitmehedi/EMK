from odoo import models, fields, api,_

class ChallanDeposited(models.TransientModel):
    _name = "challan.deposit"
    _description = "Challan Deposit"

    @api.one
    def action_deposited(self):
        self.env['tds.vendor.challan'].browse(self._context.get('active_ids')).action_deposited()