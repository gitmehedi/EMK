from odoo import models, fields, api,_


class MultiChallanApproveWizard(models.TransientModel):
    _name = "multi.challan.approve.wizard"
    _description = "Multi Challan Approve"


    @api.one
    def action_approve(self):
        self.env['tds.vat.challan'].browse(self._context.get('active_ids')).action_approve()