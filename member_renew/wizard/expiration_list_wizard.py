from datetime import datetime, timedelta

from odoo import models, fields, api, _


class ExpirationListWizard(models.TransientModel):
    _name = 'expiration.list.wizard'

    no_of_days = fields.Integer(required=True, string='No of Days')

    @api.multi
    def generate(self):
        if self.no_of_days:
            start_date = datetime.now().strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=self.no_of_days)).strftime('%Y-%m-%d')

            res = self.env['res.partner'].search(
                [('membership_stop', '>=', start_date), ('membership_stop', '<=', end_date)], order='membership_days_remaining desc')

            view_id = self.env.ref('member_renew.view_res_partner_expiration_tree')

            return {
                'name': ('Members'),
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'res.partner',
                'domain': [('id', '=', res.ids)],
                'view_id': view_id and view_id.id or False,
                'type': 'ir.actions.act_window',
            }
