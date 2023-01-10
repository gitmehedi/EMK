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
        domain=_commission_refund_account_payable_domain,
        track_visibility='onchange',
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

    def create_commission_refund_ap_account_id(self):
        config_ap_id = self.env['ir.values'].sudo().get_default('sale.config.settings', 'commission_refund_default_ap_parent_id')
        if not config_ap_id:
            raise UserError(_("Commission/Refund default AP not set on Sales/Configuration/Settings"))

        parent_acc_id = self.env['account.account'].browse(int(config_ap_id)).parent_id
        account_id = self.env['account.account'].search([('parent_id', '=', parent_acc_id.id)], limit=1, order="id desc")
        code = int(account_id.code) + 1

        vals = {
            "code": '%s' % code,
            "name": "{} - Commission/Refund AP".format(self.name),
            "company_id": self.company_id.id,
            "parent_id": parent_acc_id.id,
            "type_third_parties": "no",
            "user_type_id": account_id.user_type_id.id,
            "reconcile": True,
        }
        account_id = self.env['account.account'].create(vals)
        if account_id:
            self.commission_refund_account_payable_id = account_id.id

        return account_id

    @api.model
    def create(self, values):
        self._check_acc_constraint(values)
        res = super(ResPartner, self).create(values)

        if res.customer and not res.commission_refund_account_payable_id:
            res.create_commission_refund_ap_account_id()

        return res

    @api.multi
    def write(self, values):
        self._check_acc_constraint(values)
        return super(ResPartner, self).write(values)
