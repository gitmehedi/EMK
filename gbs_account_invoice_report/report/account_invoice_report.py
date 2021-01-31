import calendar
from odoo import tools
from odoo import models, fields, api


class GBSAccountInvoiceReport(models.Model):
    _name = "gbs.account.invoice.report"
    _description = "Analytical Invoice Report"
    _auto = False
    _rec_name = 'date'

    # Report Fields
    date = fields.Date(readonly=True)
    product_id = fields.Many2one('product.template', string='Product', readonly=True)
    product_qty = fields.Float(string='Qty (MT)', readonly=True)
    country_id = fields.Many2one('res.country', string='Country')
    sector = fields.Many2one('res.partner.category', string='Sector', readonly=True)
    supplier_type = fields.Char(string='Region (Local/Foreign)', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True)
    # company_id = fields.Many2one('res.company', string='Company', readonly=True)
    user_id = fields.Many2one('res.users', string='Sales Person', readonly=True)
    price_total = fields.Float(string='Amt (BDT)', readonly=True)
    price_average = fields.Float(string='Avg Price', readonly=True, group_operator="avg")
    # uom_name = fields.Char(string='UOM', readonly=True)
    so_name = fields.Char(string='SO Number', readonly=True)
    val_ratio = fields.Float(string='Ratio(%)', readonly=True)

    # categ_id = fields.Many2one('product.category', string='Product Category', readonly=True)
    # journal_id = fields.Many2one('account.journal', string='Journal', readonly=True)
    # payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms', oldname='payment_term', readonly=True)
    # fiscal_position_id = fields.Many2one('account.fiscal.position', oldname='fiscal_position', string='Fiscal Position', readonly=True)
    # commercial_partner_id = fields.Many2one('res.partner', string='Partner Company', help="Commercial Entity")
    # nbr = fields.Integer(string='# of Lines', readonly=True)  # TDE FIXME master: rename into nbr_lines
    # date_due = fields.Date(string='Due Date', readonly=True)
    # account_id = fields.Many2one('account.account', string='Account', readonly=True, domain=[('deprecated', '=', False)])
    # account_line_id = fields.Many2one('account.account', string='Account Line', readonly=True, domain=[('deprecated', '=', False)])
    # partner_bank_id = fields.Many2one('res.partner.bank', string='Bank Account', readonly=True)
    # residual = fields.Float(string='Total Residual', readonly=True)
    # user_currency_residual = fields.Float(string="Total Residual", compute='_compute_amounts_in_user_currency', digits=0)
    # weight = fields.Float(string='Gross Weight', readonly=True)
    # volume = fields.Float(string='Volume', readonly=True)


    # type = fields.Selection([
    #     ('out_invoice', 'Customer Invoice'),
    #     ('in_invoice', 'Vendor Bill'),
    #     ('out_refund', 'Customer Refund'),
    #     ('in_refund', 'Vendor Refund'),
    # ], readonly=True)
    # state = fields.Selection([
    #     ('draft', 'Draft'),
    #     ('proforma', 'Pro-forma'),
    #     ('proforma2', 'Pro-forma'),
    #     ('open', 'Open'),
    #     ('paid', 'Done'),
    #     ('cancel', 'Cancelled')
    # ], string='Status', readonly=True)

    _order = 'date desc'

    _depends = {
        'account.invoice': [
            'account_id', 'amount_total_company_signed', 'commercial_partner_id', 'company_id',
            'currency_id', 'date_due', 'date_invoice', 'fiscal_position_id',
            'journal_id', 'partner_bank_id', 'partner_id', 'payment_term_id',
            'residual', 'state', 'type', 'user_id',
        ],
        'account.invoice.line': [
            'account_id', 'invoice_id', 'price_subtotal', 'product_id',
            'quantity', 'uom_id', 'account_analytic_id',
        ],
        'product.product': ['product_tmpl_id'],
        'product.template': ['categ_id'],
        'product.uom': ['category_id', 'factor', 'name', 'uom_type'],
        'res.currency.rate': ['currency_id', 'name'],
        'res.partner': ['country_id'],
    }

    def _get_ratio_column(self):
        ratio_col_str = """
            , (SUM(ail.price_subtotal_signed) / 
            (SELECT SUM(ail.price_subtotal_signed) AS total_value 
        """ + self._from() + self._where() + """ ) * 100) AS ratio"""
        return ratio_col_str

    def _select(self):
        select_str = """
            SELECT
                sub.id, 
                sub.date, 
                sub.product_id, 
                sub.partner_id, 
                sub.country_id,
                sub.uom_name,
                sub.user_id, 
                sub.company_id, 
                sub.type, 
                sub.state,
                sub.so_name,
                sub.supplier_type,
                sub.sector,
                sub.product_qty, 
                sub.price_total as price_total, 
                sub.price_average,
                sub.ratio as val_ratio
        """
        return select_str

    def _sub_select(self):
        select_str = """
                SELECT
                    ail.id AS id,
                    ai.date_invoice AS date,
                    u2.name AS uom_name,
                    pt.id AS product_id,
                    ai.partner_id,
                    ai.origin as so_name,
                    ai.user_id,
                    ai.company_id,
                    ai.type,
                    ai.state,
                    SUM (ail.quantity / u.factor * u2.factor) AS product_qty,
                    SUM(ail.price_subtotal_signed) AS price_total,
                    SUM(ABS(ail.price_subtotal_signed)) / CASE
                            WHEN SUM(ail.quantity / u.factor * u2.factor) <> 0::numeric
                               THEN SUM(ail.quantity / u.factor * u2.factor)
                               ELSE 1::numeric
                            END AS price_average,
                    partner.country_id,
                    partner.supplier_type AS supplier_type,
                    rpc.id AS sector
        """ + self._get_ratio_column()
        return select_str

    def _from(self):
        from_str = """
                FROM 
                    account_invoice_line ail
                    JOIN account_invoice ai ON ai.id = ail.invoice_id AND ai.type = 'out_invoice'
                    JOIN res_partner partner ON ai.commercial_partner_id = partner.id
                    LEFT JOIN product_product pr ON pr.id = ail.product_id
                    LEFT JOIN product_template pt ON pt.id = pr.product_tmpl_id
                    LEFT JOIN product_uom u ON u.id = ail.uom_id
                    LEFT JOIN product_uom u2 ON u2.id = pt.uom_id
                    JOIN res_partner_category rpc ON partner.sector_id = rpc.id
        """
        return from_str

    @staticmethod
    def subtract_date(date_now, year=0, month=0):
        dt = fields.Date.from_string(date_now)
        year, month = divmod(year * 12 + month, 12)
        if dt.month <= month:
            year = dt.year - year - 1
            month = dt.month - month + 12
        else:
            year = dt.year - year
            month = dt.month - month
        return dt.replace(year=year, month=month, day=1)

    def _where(self):
        date_now = fields.Date.today()
        date_from = self.subtract_date(date_now, month=2)
        # From date string
        date_from_str = str(date_from.year) + '-' + str(date_from.month) + '-01'
        date_to = fields.Date.from_string(date_now)
        _, last_day = calendar.monthrange(date_to.year, date_to.month)
        # To date string
        date_to_str = str(date_to.year) + '-' + str(date_to.month) + '-' + str(last_day)

        where_str = """
               WHERE ai.state in ('open','paid') AND pt.active = true AND ai.date_invoice BETWEEN '%s' and '%s'
        """ % (date_from_str, date_to_str)
        return where_str

    def _group_by(self):
        group_by_str = """
                GROUP BY 
                    ail.id, 
                    ai.date_invoice,
                    u2.name,
                    pt.id,  
                    ai.id,
                    ai.partner_id,
                    ai.origin, 
                    ai.user_id, 
                    ai.company_id,
                    ai.type,
                    ai.state,
                    partner.country_id,
                    partner.supplier_type,
                    rpc.id
        """
        return group_by_str

    @api.model_cr
    def init(self):
        # self._table = account_invoice_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE or REPLACE VIEW %s AS (
                %s
                FROM (
                    %s %s %s %s
                ) AS sub
            )""" % (self._table, self._select(), self._sub_select(), self._from(), self._where(), self._group_by()))
