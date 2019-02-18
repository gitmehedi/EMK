from odoo import models, fields, api,_


class ChallanDistributed(models.TransientModel):
    _name = "challan.distribute"
    _description = "Challan Distribute"


    @api.one
    def action_distributed(self):
        self.env['tds.vat.challan'].browse(self._context.get('active_ids')).action_distributed()