
from odoo import api, models, _
from odoo.exceptions import UserError


class InvoiceMerge(models.TransientModel):
    _inherit = "invoice.merge"

    @api.model
    def _dirty_check(self):
        res = super(InvoiceMerge, self)._dirty_check()
        if self.env.context.get('active_model', '') == 'account.invoice':
            ids = self.env.context['active_ids']
            invs = self.env['account.invoice'].browse(ids)
            for d in invs:
                if d.agreement_id:
                    if d['agreement_id'] != invs[0]['agreement_id']:
                        raise UserError(_('Not all Invoice are at the same '
                                      'Agreement!'))
        return res
