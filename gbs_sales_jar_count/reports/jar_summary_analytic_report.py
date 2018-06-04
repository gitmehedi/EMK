from odoo import tools
from odoo import models, fields, api


class JarSummaryAnalyticReport(models.Model):
    _name = "jar.summary.analytic.report"
    _description = "JAR Summary Analytic Report"
    _auto = False
    _rec_name = 'partner_id'


    partner_id = fields.Many2one('res.partner', string='Customer', domain=[('customer', '=', True)], required=True)
    total_jar_taken = fields.Integer(string='Total Jar Taken')
    jar_received = fields.Integer(string='Jar Received')
    jar_received_date = fields.Datetime(string='Jar Received Date')
    uom_id = fields.Many2one('product.uom', string='UoM')
    due_jar = fields.Integer(string='Due Jar', compute='_calculate_number_of_due_jar')


    @api.model
    def _calculate_number_of_due_jar(self):
        for jar in self:
            jar.due_jar = jar.total_jar_taken - jar.jar_received


    # date = fields.Date(readonly=True)
    # product_id = fields.Many2one('product.product', string='Product', readonly=True)
    # product_qty = fields.Float(string='Product Quantity', readonly=True)
    # uom_name = fields.Char(string='Reference Unit of Measure', readonly=True)
    # payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms', oldname='payment_term',
    #                                   readonly=True)
    # fiscal_position_id = fields.Many2one('account.fiscal.position', oldname='fiscal_position', string='Fiscal Position',
    #                                      readonly=True)
    # currency_id = fields.Many2one('res.currency', string='Currency', readonly=True)
    # categ_id = fields.Many2one('product.category', string='Product Category', readonly=True)
    # journal_id = fields.Many2one('account.journal', string='Journal', readonly=True)
    # partner_id = fields.Many2one('res.partner', string='Customer', readonly=True)
    # commercial_partner_id = fields.Many2one('res.partner', string='Partner Company', help="Commercial Entity")
    # company_id = fields.Many2one('res.company', string='Company', readonly=True)
    # user_id = fields.Many2one('res.users', string='Salesperson', readonly=True)
    # price_average = fields.Float(string='Average Price', readonly=True, group_operator="avg")
    # user_currency_price_average = fields.Float(string="Average Price", compute='_compute_amounts_in_user_currency',
    #                                            digits=0)
    # currency_rate = fields.Float(string='Currency Rate', readonly=True, group_operator="avg")
    # nbr = fields.Integer(string='# of Lines', readonly=True)
    #
    # price_total = fields.Float(string='Total Invoice Amount Without Tax', readonly=True)
    # user_currency_price_total = fields.Float(string="Total Invoice Amount Without Tax",
    #                                          compute='_compute_amounts_in_user_currency', digits=0)
    #
    # date_due = fields.Date(string='Due Date', readonly=True)
    # account_id = fields.Many2one('account.account', string='Account', readonly=True,
    #                              domain=[('deprecated', '=', False)])
    # account_line_id = fields.Many2one('account.account', string='Account Line', readonly=True,
    #                                   domain=[('deprecated', '=', False)])
    # partner_bank_id = fields.Many2one('res.partner.bank', string='Bank Account', readonly=True)
    # residual = fields.Float(string='Total Due Amount', readonly=True)
    # user_currency_residual = fields.Float(string="Total Residual", compute='_compute_amounts_in_user_currency',
    #                                       digits=0)
    # country_id = fields.Many2one('res.country', string='Country of the Partner Company')
    # weight = fields.Float(string='Gross Weight', readonly=True)
    # volume = fields.Float(string='Volume', readonly=True)
    # commission = fields.Float(string='Total Commission', readonly=True)
    # type = fields.Selection([
    #     ('out_invoice', 'Customer Invoice'),
    #     ('in_invoice', 'Vendor Bill'),
    #     ('out_refund', 'Customer Refund'),
    #     ('in_refund', 'Vendor Refund'),
    # ], readonly=True)
    #
    # state = fields.Selection([
    #     ('draft', 'Draft'),
    #     ('proforma', 'Pro-forma'),
    #     ('proforma2', 'Pro-forma'),
    #     ('open', 'Open'),
    #     ('paid', 'Done'),
    #     ('cancel', 'Cancelled')
    # ], string='Invoice Status', readonly=True)

    _order = 'jar_received_date desc'

    # _depends = {
    #     'account.invoice': [
    #         'account_id', 'amount_total_company_signed', 'commercial_partner_id', 'company_id',
    #         'currency_id', 'date_due', 'date_invoice', 'fiscal_position_id',
    #         'journal_id', 'partner_bank_id', 'partner_id', 'payment_term_id',
    #         'residual', 'state', 'type', 'user_id', 'generated_commission_amount',
    #     ],
    #     'account.invoice.line': [
    #         'account_id', 'invoice_id', 'price_subtotal', 'product_id',
    #         'quantity', 'uom_id', 'account_analytic_id',
    #     ],
    #     'product.product': ['product_tmpl_id'],
    #     'product.template': ['categ_id'],
    #     'product.uom': ['category_id', 'factor', 'name', 'uom_type'],
    #     'res.currency.rate': ['currency_id', 'name'],
    #     'res.partner': ['country_id'],
    # }
    #
    # def _select(self):
    #     select_str = """
    #         SELECT *
    #     """
    #     return select_str
    #
    # def _sub_select(self):
    #     select_str = """
    #             SELECT ail.id AS id,
    #                 ai.date_invoice AS date,
    #                 ail.product_id, ai.partner_id, ai.payment_term_id, ail.account_analytic_id,
    #                 u2.name AS uom_name,
    #                 ai.currency_id, ai.journal_id, ai.fiscal_position_id, ai.user_id, ai.company_id,
    #                 1 AS nbr,
    #                 ai.type, ai.state, pt.categ_id, ai.date_due, ai.account_id, ail.account_id AS account_line_id,
    #                 ai.partner_bank_id,
    #                 ai.generated_commission_amount,
    #                 SUM ((invoice_type.sign * ail.quantity) / u.factor * u2.factor) AS product_qty,
    #                 SUM(ail.price_subtotal_signed * invoice_type.sign) AS price_total,
    #                 SUM(ABS(ail.price_subtotal_signed)) / CASE
    #                         WHEN SUM(ail.quantity / u.factor * u2.factor) <> 0::numeric
    #                            THEN SUM(ail.quantity / u.factor * u2.factor)
    #                            ELSE 1::numeric
    #                         END AS price_average,
    #                 ai.residual_company_signed / (SELECT count(*) FROM account_invoice_line l where invoice_id = ai.id) *
    #                 count(*) * invoice_type.sign AS residual,
    #                 ai.commercial_partner_id as commercial_partner_id,
    #                 partner.country_id,
    #                 SUM(pr.weight * (invoice_type.sign*ail.quantity) / u.factor * u2.factor) AS weight,
    #                 SUM(pr.volume * (invoice_type.sign*ail.quantity) / u.factor * u2.factor) AS volume
    #     """
    #     return select_str
    #
    # def _from(self):
    #     from_str = """
    #             FROM uom_jar_summary
    #     """
    #     return from_str
    #
    # def _group_by(self):
    #     group_by_str = """
    #             GROUP BY
    #     """
    #     return group_by_str
    #

    @api.model_cr
    def init(self):
        # self._table = account_invoice_report
        #tools.drop_view_if_exists(self.env.cr, self._table)
        # sql = """CREATE or REPLACE VIEW %s as (
        #     WITH currency_rate AS (%s)
        #     %s
        #     FROM (
        #         %s %s %s
        #     ) AS sub
        #     LEFT JOIN currency_rate cr ON
        #         (cr.currency_id = sub.currency_id AND
        #          cr.company_id = sub.company_id AND
        #          cr.date_start <= COALESCE(sub.date, NOW()) AND
        #          (cr.date_end IS NULL OR cr.date_end > COALESCE(sub.date, NOW())))
        # )""" % (
        #     self._table, self.env['res.currency']._select_companies_rates(),
        #     self._select(), self._sub_select(), self._from(), self._group_by())

        sql1 = """CREATE or REPLACE VIEW temp_jar as SELECT * from uom_jar_summary"""
        self.env.cr.execute(sql1)
