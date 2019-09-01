import calendar
from odoo import tools
from odoo import models, fields, api


class GBSAccountInvoiceReport(models.Model):
    _name = "gbs.account.invoice.report"
    _description = "Analytical Invoice Report"
    _auto = False
    _rec_name = 'date'

    @api.multi
    @api.depends('currency_id', 'date', 'price_total', 'price_average')
    def _compute_amounts_in_user_currency(self):
        """Compute the amounts in the currency of the user
        """
        context = dict(self._context or {})
        user_currency_id = self.env.user.company_id.currency_id
        currency_rate_id = self.env['res.currency.rate'].search([
            ('rate', '=', 1),
            '|', ('company_id', '=', self.env.user.company_id.id), ('company_id', '=', False)], limit=1)
        base_currency_id = currency_rate_id.currency_id
        ctx = context.copy()
        for record in self:
            ctx['date'] = record.date
            record.user_currency_price_total = base_currency_id.with_context(ctx).compute(record.price_total, user_currency_id)
            record.user_currency_price_average = base_currency_id.with_context(ctx).compute(record.price_average, user_currency_id)


    date = fields.Date(readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    product_qty = fields.Float(string='Quantity', readonly=True)
    country_id = fields.Many2one('res.country', string='Country')
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True)
    sector = fields.Many2one('res.partner.category', string='Sector', readonly=True)
    supplier_type = fields.Char(string='Region', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    user_id = fields.Many2one('res.users', string='Salesperson', readonly=True)
    price_total = fields.Float(string='Value', readonly=True)
    user_currency_price_total = fields.Float(string="Value", compute='_compute_amounts_in_user_currency', digits=0)
    price_average = fields.Float(string='Avg Price', readonly=True, group_operator="avg")
    user_currency_price_average = fields.Float(string="Avg Price", compute='_compute_amounts_in_user_currency',digits=0)
    currency_rate = fields.Float(string='Currency Rate', readonly=True, group_operator="avg")
    uom_name = fields.Char(string='UOM', readonly=True)
    so_name = fields.Char(string='SO Number', readonly=True)

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


    type = fields.Selection([
        ('out_invoice', 'Customer Invoice'),
        ('in_invoice', 'Vendor Bill'),
        ('out_refund', 'Customer Refund'),
        ('in_refund', 'Vendor Refund'),
    ], readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('proforma', 'Pro-forma'),
        ('proforma2', 'Pro-forma'),
        ('open', 'Open'),
        ('paid', 'Done'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True)

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

    def _select(self):
        select_str = """
            SELECT sub.id, sub.date, sub.product_id, sub.partner_id, sub.country_id,sub.uom_name,
                sub.currency_id,sub.user_id, sub.company_id, sub.type, sub.state,sub.so_name,
                sub.supplier_type,sub.sector,sub.product_qty, sub.price_total as price_total, 
                sub.price_average as price_average,COALESCE(cr.rate, 1) as currency_rate
        """
        return select_str

    def _sub_select(self):
        select_str = """
                SELECT ail.id AS id,
                    ai.date_invoice AS date,u2.name AS uom_name,
                    ail.product_id, ai.partner_id,ai.origin as so_name,
                    ai.currency_id, ai.user_id, 
                    ai.company_id,ai.type, ai.state,
                    SUM ((invoice_type.sign * ail.quantity) / u.factor * u2.factor) AS product_qty,
                    SUM(ail.price_subtotal_signed * invoice_type.sign) AS price_total,
                    SUM(ABS(ail.price_subtotal_signed)) / CASE
                            WHEN SUM(ail.quantity / u.factor * u2.factor) <> 0::numeric
                               THEN SUM(ail.quantity / u.factor * u2.factor)
                               ELSE 1::numeric
                            END AS price_average,
                    partner.country_id,
                    partner.supplier_type AS supplier_type,
                    rpc.id AS sector
        """
        return select_str

    def _from(self):
        from_str = """
                FROM account_invoice_line ail
                JOIN account_invoice ai ON ai.id = ail.invoice_id
                JOIN res_partner partner ON ai.commercial_partner_id = partner.id
                LEFT JOIN product_product pr ON pr.id = ail.product_id
                LEFT JOIN product_template pt ON pt.id = pr.product_tmpl_id
                LEFT JOIN product_uom u ON u.id = ail.uom_id
                LEFT JOIN product_uom u2 ON u2.id = pt.uom_id
                JOIN res_partner_category rpc ON partner.sector_id = rpc.id
                JOIN (
                    -- Temporary table to decide if the qty should be added or retrieved (Invoice vs Refund) 
                    SELECT id,(CASE
                         WHEN ai.type::text = ANY (ARRAY['in_refund'::character varying::text, 'in_invoice'::character varying::text])
                            THEN -1
                            ELSE 1
                        END) AS sign
                    FROM account_invoice ai
                ) AS invoice_type ON invoice_type.id = ai.id
        """
        return from_str

    def _where(self):
        date_now = fields.Date.today()
        year_now = fields.Date.from_string(date_now).year
        to_month_num = fields.Date.from_string(date_now).month
        from_month_num = fields.Date.from_string(date_now).month - 2
        last_day = calendar.monthrange(year_now, to_month_num)
        to_month_format = str(year_now)+'-'+str(to_month_num)+'-'+str(last_day[1])
        from_month_format = str(year_now)+'-'+str(from_month_num)+'-01'
        where_str = """
               where ai.state in ('open','paid') and ai.date_invoice BETWEEN '%s' and '%s'
        """% (from_month_format, to_month_format)
        return where_str


    def _group_by(self):
        group_by_str = """
                GROUP BY ail.id, ail.product_id, ai.date_invoice, ai.id,u2.name,
                    ai.partner_id, ai.currency_id,ai.origin,
                    ai.user_id, ai.company_id, ai.type, invoice_type.sign, ai.state,
                    partner.country_id,rpc.id,partner.supplier_type
        """
        return group_by_str

    @api.model_cr
    def init(self):
        # self._table = account_invoice_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            WITH currency_rate AS (%s)
            %s
            FROM (
                %s %s %s %s
            ) AS sub
            LEFT JOIN currency_rate cr ON
                (cr.currency_id = sub.currency_id AND
                 cr.company_id = sub.company_id AND
                 cr.date_start <= COALESCE(sub.date, NOW()) AND
                 (cr.date_end IS NULL OR cr.date_end > COALESCE(sub.date, NOW())))
        )""" % (self._table, self.env['res.currency']._select_companies_rates(),
                self._select(), self._sub_select(), self._from(),self._where(),self._group_by()))