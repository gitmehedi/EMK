from odoo import models, fields, api,_
from odoo.exceptions import UserError


class ChallanDistributed(models.TransientModel):
    _name = "challan.distribute"
    _description = "Challan Distribute"


    @api.one
    def action_distributed(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['tds.vendor.challan'].browse(active_ids):
            if record.state not in ('deposited'):
                raise UserError(
                    _("Selected invoice(s) cannot be deposited as they are not in 'Draft' state."))
            for line in record.line_ids:
                line.write({'state': 'deposited', 'challan_provided': line.undistributed_bill})
            res = {
                'state': 'distributed',
                'distribute_approver': self.env.user.id,
                'distribute_date': fields.Datetime.now(),
            }
            record.write(res)
