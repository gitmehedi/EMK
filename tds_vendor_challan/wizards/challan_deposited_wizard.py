from odoo import models, fields, api,_
from odoo.exceptions import UserError


class ChallanDeposit(models.TransientModel):
    _name = "challan.deposit"
    _description = "Challan Deposit"

    @api.one
    def action_deposited(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['tds.vendor.challan'].browse(active_ids):
            if record.state not in ('draft'):
                raise UserError(
                    _("Selected invoice(s) cannot be deposited as they are not in 'Draft' state."))
            for line in record.line_ids:
                line.write({'state': 'deposited', 'challan_provided': line.undistributed_bill})
            res = {
                'state': 'deposited',
                'deposit_approver': self.env.user.id,
                'deposit_date': fields.Datetime.now(),
            }
            record.write(res)
