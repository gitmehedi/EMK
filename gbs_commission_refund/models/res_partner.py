from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.depends('commission_refund_account_payable_id')
    def _commission_refund_account_payable_domain(self):
        customer_ids = self.env['res.partner'].search([
            ('active', '=', True),
            ('customer', '=', True),
            ('commission_refund_account_payable_id', '!=', False)
        ])

        domain = [("id", "!=", [c.commission_refund_account_payable_id.id for c in customer_ids]), ('internal_type', '=', 'payable')]
        return domain

    commission_refund_account_payable_id = fields.Many2one(
        comodel_name='account.account',
        string='Account Payable for Commission and Refund',
        domain=_commission_refund_account_payable_domain
    )

    def _check_acc_constraint(self, values):
        if values.get('commission_refund_account_payable_id'):
            customer_id = self.env['res.partner'].search([
                ('active', '=', True),
                ('customer', '=', True),
                ('commission_refund_account_payable_id', '=', values['commission_refund_account_payable_id'])
            ])

            if customer_id:
                raise UserError(_('Selected Account Payable for Commission and Refund already used for another customer.'))

    @api.model
    def create(self, values):
        self._check_acc_constraint(values)
        return super(ResPartner, self).create(values)

    @api.multi
    def write(self, values):
        self._check_acc_constraint(values)
        return super(ResPartner, self).write(values)
