from collections import defaultdict

# imports of odoo
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class CommissionAndRefundAccountConfig(models.Model):
    _inherit = ['mail.thread']

    _name = 'commission.refund.acc.config'
    _description = 'Commission and Refund Journal Config'
    _rec_name = "company_id"

    commission_account_id = fields.Many2one('account.account', string='Default Commission Account', track_visibility="onchange")
    commission_control_account_id = fields.Many2one('account.account', string='Default Commission Control Account', track_visibility="onchange")

    refund_account_id = fields.Many2one('account.account', string='Default Refund Account', track_visibility="onchange")
    refund_control_account_id = fields.Many2one('account.account', string='Default Refund Control Account', track_visibility="onchange")

    def _get_allowed_company_ids(self):
        domain = [("id", "in", self.env.user.company_ids.ids)]
        return domain

    company_id = fields.Many2one('res.company', string="Company", track_visibility="onchange", domain=_get_allowed_company_ids)

    def _get_allowed_hr_department_ids(self):
        domain = [("company_id", "in", self.env.user.company_ids.ids)]
        return domain

    department_id = fields.Many2one('hr.department', string="Department", track_visibility="onchange", domain=_get_allowed_hr_department_ids)

    # operating_unit_id = fields.Many2one('operating.unit', string="Operating Unit", track_visibility="onchange")

    commission_account_ids = fields.One2many('commission.account.line', 'commission_config_id', 'Commission Accounts')
    refund_account_ids = fields.One2many('refund.account.line', 'refund_config_id', 'Refund Accounts')

    _sql_constraints = [('company_id_uniq', 'unique(company_id)', 'A settings is already exist for selected company.')]

    @api.onchange('company_id')
    def onchange_company_id_department_domain(self):
        self.department_id = [(5, 0, 0)]
        return {'domain': {'department_id': [('company_id', '=', self.company_id.id)]}}


class CommissionAccount(models.Model):
    _name = "commission.account.line"
    _description = "Commission Account"

    cost_center_id = fields.Many2one('account.cost.center', string="Cost Center")
    zone_type = fields.Selection(string='Zone', selection=[('local', 'Local'), ('foreign', 'Foreign')])
    account_id = fields.Many2one('account.account', string='Default Commission Account')

    commission_config_id = fields.Many2one('commission.refund.acc.config', string="Commission Refund Config")


class RefundAccount(models.Model):
    _name = "refund.account.line"
    _description = "Refund Account"

    cost_center_id = fields.Many2one('account.cost.center', string="Cost Center")
    zone_type = fields.Selection(string='Zone', selection=[('local', 'Local'), ('foreign', 'Foreign')])
    account_id = fields.Many2one('account.account', string='Default Refund Account')

    refund_config_id = fields.Many2one('commission.refund.acc.config', string="Commission Refund Config")
