from odoo import models, fields, api


class AccountBankStatementManual(models.Model):
    _name = "account.bank.statement.manual"
    _description = "Bank Statement Line Manual Operation"

    sequence = fields.Integer()
    statement_id = fields.Many2one('account.bank.statement', ondelete='cascade')
    currency_id = fields.Many2one(related='statement_id.currency_id')
    company_id = fields.Many2one(related='statement_id.company_id')
    account_id = fields.Many2one('account.account', domain="[('deprecated', '=', False)]", check_company=True)

    @api.depends('account_id')
    def account_type_calc(self):
        for rec in self:
            if rec.account_id:
                if rec.account_id.user_type_id:
                    rec.account_type_id = rec.account_id.user_type_id.id
                    rec.account_type_id_partner_req = rec.account_id.user_type_id.partner_required
                    rec.account_type_id_cost_center_req = rec.account_id.user_type_id.cost_center_required
                    rec.account_type_id_dept_req = rec.account_id.user_type_id.department_required
                    rec.account_type_id_ou_req = rec.account_id.user_type_id.operating_unit_required
                    rec.account_type_id_analytic_acc_req = rec.account_id.user_type_id.analytic_account_required

    account_type_id = fields.Many2one('account.account.type', compute='account_type_calc', store=False)
    account_type_id_partner_req = fields.Boolean(compute='account_type_calc', store=False)
    account_type_id_cost_center_req = fields.Boolean(compute='account_type_calc', store=False)
    account_type_id_dept_req = fields.Boolean(compute='account_type_calc', store=False)
    account_type_id_ou_req = fields.Boolean(compute='account_type_calc', store=False)
    account_type_id_analytic_acc_req = fields.Boolean(compute='account_type_calc', store=False)

    name = fields.Char(string='Label')

    @api.depends('statement_id')
    def calculate_balance(self):
        for rec in self:
            if rec.statement_id:
                rec.balance = rec.statement_id.matched_balance

    balance = fields.Monetary('Amount', compute='calculate_balance')

    def _get_partner(self):
        partners = self.env['res.partner'].search(
            ['|', ('customer', '=', True), ('supplier', '=', True), ('active', '=', True), ('parent_id', '=', False)])
        domain = [("id", "in", partners.ids)]
        return domain

    partner_id = fields.Many2one('res.partner', domain=_get_partner)
    tax_ids = fields.Many2many('account.tax', string='Taxes', help="Taxes that apply on the base amount",
                               check_company=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', check_company=True)
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags', check_company=True)

    product_id = fields.Many2one('product.product', string='Product')

    tax_tag_ids = fields.Many2many(string="Tags", comodel_name='account.account.tag', ondelete='restrict',
                                   help="Tags assigned to this line by the tax creating it, if any. It determines its impact on financial reports.")

    tax_repartition_line_id = fields.Many2one(comodel_name='account.tax.repartition.line',
                                              string="Originator Tax Distribution Line", ondelete='restrict',
                                              readonly=True,
                                              check_company=True,
                                              help="Tax distribution line that caused the creation of this move line, if any")
    auto_tax_line = fields.Boolean()

    tax_line_id = fields.Many2one("account.bank.statement.manual", readonly=True, ondelete='cascade')

    cost_center_id = fields.Many2one('account.cost.center', string="Cost Center")

    def _get_department(self):
        user_company = self.env.user.company_id
        departments = self.env['hr.department'].search([('company_id', '=', user_company.id)])
        domain = [("id", "in", departments.ids)]
        return domain
    department_id = fields.Many2one("hr.department", string="Department", domain=_get_department)

    def _get_operating_unit(self):
        domain = [("id", "in", self.env.user.operating_unit_ids.ids)]
        return domain

    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit', domain=_get_operating_unit)

    @api.onchange('account_id')
    def _onchange_account_id(self):
        if self.account_id and not self.name:
            self.name = self.account_id.name
