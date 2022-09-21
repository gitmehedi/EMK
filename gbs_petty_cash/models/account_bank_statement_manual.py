from odoo import models, fields, api


class AccountBankStatementManual(models.Model):
    _name = "account.bank.statement.manual"
    _description = "Bank Statement Line Manual Operation"

    sequence = fields.Integer()
    statement_id = fields.Many2one('account.bank.statement', ondelete='cascade')
    currency_id = fields.Many2one(related='statement_id.currency_id')
    company_id = fields.Many2one(related='statement_id.company_id')
    account_id = fields.Many2one('account.account', domain="[('deprecated', '=', False)]", check_company=True)
    name = fields.Char(string='Label')

    @api.depends('statement_id')
    def calculate_balance(self):
        for rec in self:
            if rec.statement_id:
                rec.balance = rec.statement_id.matched_balance

    balance = fields.Monetary('Amount', compute='calculate_balance')
    partner_id = fields.Many2one('res.partner')
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

    department_id = fields.Many2one("hr.department", string="Department")

    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit')

    # @api.multi
    # @api.depends('statement_id', 'statement_line_id')
    # def compute_balance(self):
    #     for rec in self:
    #         if rec.statement_id:
    #             rec.balance = rec.statement_id.matched_balance
    #         elif rec.statement_line_id:
    #             rec.balance = rec.statement_line_id.matched_balance

    # @api.multi
    # @api.onchange('balance')
    # def _onchange_statement_line_id(self):
    #     if not self.balance:
    #         if self.statement_line_id:
    #             self.balance = self.statement_line_id.matched_balance
    #         elif self.statement_id:
    #             self.balance = self.statement_id.matched_balance
    @api.onchange('account_id')
    def _onchange_account_id(self):
        if self.account_id and not self.name:
            self.name = self.account_id.name
