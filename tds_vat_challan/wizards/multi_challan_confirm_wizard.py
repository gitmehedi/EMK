from odoo import models, fields, api,_

class MultiChallanConfirmWizard(models.TransientModel):
    _name = "multi.challan.confirm.wizard"
    _description = "Multi Challan Confirm"

    @api.one
    def action_confirm(self):
        self.env['tds.vat.challan'].browse(self._context.get('active_ids')).action_confirm()