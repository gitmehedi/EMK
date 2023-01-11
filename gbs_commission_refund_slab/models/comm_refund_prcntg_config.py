from odoo import fields, models, api, _
import time
from datetime import timedelta, datetime
from odoo.exceptions import UserError, ValidationError


def _date_range():
    date_today = datetime.now().date()
    month_first_day = date_today.replace(day=1)
    last_month_last_date = (month_first_day - timedelta(days=1))
    last_month_first_date = last_month_last_date.replace(day=1)

    return last_month_first_date, last_month_last_date


class CommissionRefundPercentageConfig(models.Model):
    _name = 'commission.refund.prcntg.config'
    _description = 'Commission Refund Percentage Configuration'

    name = fields.Char(readonly=True)
    type = fields.Selection([('Monthly', 'Monthly'), ('Yearly', 'Yearly')],
                            string='Type', required=True, default='Monthly')

    fiscal_month = fields.Many2one('date.range', string='Fiscal Month/Year', required=True)
    cron_executed = fields.Boolean(default=False, string="Cron Executed")

    @api.model
    def create(self, vals):
        if vals['fiscal_month'] and vals['type']:
            date_range = self.env['date.range'].sudo().browse(vals['fiscal_month'])
            vals['name'] = vals['type'] + ': ' + date_range.name
        return super(CommissionRefundPercentageConfig, self).create(vals)

    @api.depends('fiscal_month')
    def compute_date(self):
        for rec in self:
            if rec.fiscal_month:
                rec.start_date = rec.fiscal_month.date_start
                rec.end_date = rec.fiscal_month.date_end
                date_end = datetime.strptime(rec.fiscal_month.date_end, '%Y-%m-%d')
                rec.cron_process_date = date_end + timedelta(days=1)

    # This code will also work instead of compute field.
    # start_date = fields.Date(related="fiscal_month.date_start")
    # end_date = fields.Date(related="fiscal_month.date_end")

    start_date = fields.Date(compute='compute_date', store=True)
    end_date = fields.Date(compute='compute_date', store=True)
    cron_process_date = fields.Date(compute_date='compute_date', store=True)

    company_id = fields.Many2one('res.company', string='Company')

    commission_line_ids = fields.One2many('commission.prcntg.config.line', 'parent_id')
    refund_line_ids = fields.One2many('refund.prcntg.config.line', 'parent_id')

    _sql_constraints = [
        ('type_fiscal_month_company',
         'unique(type,fiscal_month,company_id)',
         'A configuration already exist.'
         )
    ]

    def _get_fiscal_year_date_range(self, date_from):
        cr = self.env.cr

        date_start, date_end = False, False

        sql = """SELECT dr.date_start, dr.date_end 
                 FROM date_range dr 
                 LEFT JOIN date_range_type drt ON drt.id = dr.type_id 
                 WHERE drt.fiscal_year = true AND dr.date_start <= %s AND dr.date_end >= %s"""

        cr.execute(sql, (date_from, date_from))

        for row in cr.dictfetchall():
            date_start = row['date_start']
            date_end = row['date_end']

        return date_start, date_end

    def _get_account_move_entry(self, accounts, init_balance, display_account, used_context):
        cr = self.env.cr
        aml_obj = self.env['account.move.line']
        move_lines = dict(map(lambda x: (x, []), accounts.ids))
        state = used_context['state']
        partner_id = used_context['partner_id']

        # Prepare initial sql query and Get the initial move lines
        if init_balance:
            fy_date_start, fy_date_end = self._get_fiscal_year_date_range(used_context['date_from'])
            journal_ids = self.env['account.journal'].search([('type', '=', 'situation')])
            init_balance_line = {'lid': 0, 'lpartner_id': '', 'account_id': accounts.ids[0], 'invoice_type': '',
                                 'invoice_id': '', 'currency_id': None, 'move_name': '', 'lname': 'Opening Balance',
                                 'debit': 0.0, 'credit': 0.0, 'balance': 0.0, 'mmove_id': '', 'partner_name': '',
                                 'currency_code': '', 'lref': '', 'amount_currency': None, 'invoice_number': '',
                                 'lcode': '', 'ldate': ''}

            # OPENING BALANCE
            sql = """SELECT 
                            l.account_id AS account_id, 
                            COALESCE(SUM(l.debit),0.0) AS debit, 
                            COALESCE(SUM(l.credit),0.0) AS credit, 
                            COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance     
                        FROM 
                            account_move_line l
                            LEFT JOIN account_move m ON (l.move_id=m.id)
                            LEFT JOIN res_partner p ON (l.partner_id=p.id)
                            JOIN account_journal j ON (l.journal_id=j.id)
                        WHERE 
                            l.account_id IN %s AND l.partner_id=%s 
                            AND l.date BETWEEN %s AND %s AND l.journal_id IN %s
            """

            sql += " AND m.state=%s GROUP BY l.account_id" if state == 'posted' else " GROUP BY l.account_id"

            if state == 'posted':
                params = (tuple(accounts.ids), partner_id, fy_date_start, fy_date_end, tuple(journal_ids.ids), state)
            else:
                params = (tuple(accounts.ids), partner_id, fy_date_start, fy_date_end, tuple(journal_ids.ids))

            cr.execute(sql, params)

            for row in cr.dictfetchall():
                init_balance_line['account_id'] = row['account_id']
                init_balance_line['debit'] = row['debit']
                init_balance_line['credit'] = row['credit']
                init_balance_line['balance'] = row['balance']

            # ADD BALANCE WITH OPENING BALANCE
            sql = """SELECT 
                            l.account_id AS account_id, 
                            COALESCE(SUM(l.debit),0.0) AS debit, 
                            COALESCE(SUM(l.credit),0.0) AS credit, 
                            COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance     
                        FROM 
                            account_move_line l
                            LEFT JOIN account_move m ON (l.move_id=m.id)
                            LEFT JOIN res_currency c ON (l.currency_id=c.id)
                            LEFT JOIN res_partner p ON (l.partner_id=p.id)
                            LEFT JOIN account_invoice i ON (m.id =i.move_id)
                            JOIN account_journal j ON (l.journal_id=j.id)
                        WHERE 
                            l.account_id IN %s AND l.partner_id=%s
                            AND l.date < %s AND l.date >= %s AND l.journal_id IN %s
            """
            sql += " AND m.state=%s GROUP BY l.account_id" if state == 'posted' else " GROUP BY l.account_id"

            if state == 'posted':
                params = (tuple(accounts.ids), partner_id, used_context['date_from'], fy_date_start, tuple(used_context['journal_ids']), state)
            else:
                params = (tuple(accounts.ids), partner_id, used_context['date_from'], fy_date_start, tuple(used_context['journal_ids']))

            cr.execute(sql, params)

            for row in cr.dictfetchall():
                init_balance_line['debit'] += row['debit']
                init_balance_line['credit'] += row['credit']
                init_balance_line['balance'] += row['balance']

            move_lines[init_balance_line.pop('account_id')].append(init_balance_line)

        sql_sort = 'l.date, l.move_id'

        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = aml_obj.with_context(used_context)._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        filters = filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')

        # Get move lines base on sql query and Calculate the total balance of move lines
        sql = ('''SELECT l.id AS lid, i.origin, invl.price_unit, invl.quantity AS qty, u.name AS unit_name, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.currency_id, l.amount_currency, l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,\
                    m.name AS move_name, c.symbol AS currency_code, p.name AS partner_name\
                    FROM account_move_line l\
                    JOIN account_move m ON (l.move_id=m.id)\
                    LEFT JOIN res_currency c ON (l.currency_id=c.id)\
                    LEFT JOIN res_partner p ON (l.partner_id=p.id)\
                    LEFT JOIN account_invoice i ON (m.id =i.move_id)\
                    LEFT JOIN account_invoice_line invl ON (i.id=invl.invoice_id)\
                    LEFT JOIN product_uom u ON (invl.uom_id=u.id)\
                    JOIN account_journal j ON (l.journal_id=j.id)\
                    JOIN account_account acc ON (l.account_id = acc.id) \
                    WHERE l.partner_id=%s AND l.account_id IN %s ''' + filters + ''' GROUP BY l.id, i.origin, invl.price_unit, invl.quantity, u.name, l.account_id, l.date, j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, c.symbol, p.name ORDER BY ''' + sql_sort)
        params = (partner_id, tuple(accounts.ids),) + tuple(where_params)
        cr.execute(sql, params)

        for row in cr.dictfetchall():
            balance = 0
            for line in move_lines.get(row['account_id']):
                balance += line['debit'] - line['credit']
            row['balance'] += balance
            move_lines[row.pop('account_id')].append(row)

        # Calculate the debit, credit and balance for Accounts
        account_res = []
        for account in accounts:
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            res['code'] = account.code
            res['name'] = account.name
            res['move_lines'] = move_lines[account.id]
            for line in res.get('move_lines'):
                res['debit'] += line['debit']
                res['credit'] += line['credit']
                res['balance'] = line['balance']
            if display_account == 'all':
                account_res.append(res)
            if display_account == 'movement' and res.get('move_lines'):
                account_res.append(res)
            if display_account == 'not_zero' and not currency.is_zero(res['balance']):
                account_res.append(res)

        return account_res

    @api.model
    def pull_automation_monthly(self):
        # TODO:company id
        # TODO: fill-up False data later on.

        so_process_config = self.env['commission.configuration'].search([('process', '=', 'checkbox')], limit=1)
        customers = self.env['res.partner'].search([('business_type', '=', so_process_config.customer_type.id)])
        journal_ids = self.env['account.journal'].search([('type', '!=', 'situation'), ('code', 'not in', ['COMJNL', 'REFJNL', 'COMJNLTP', 'REFJNLTP'])])

        start_date, end_date = _date_range()
        percentage_config = self.env['commission.refund.prcntg.config'].search([
            ('company_id', '=', so_process_config.company_id.id),
            ('start_date', '=', start_date),
            ('end_date', '=', end_date),
            ('type', '=', 'Monthly'),
        ], limit=1)

        if not percentage_config:
            print("No monthly slab configuration found for date range (%s to %s)" % (start_date, end_date))
            return

        if percentage_config.cron_executed:
            print("The job was already executed for the range (%s to %s)" % (start_date, end_date))
            return

        journal_id = self.env['account.journal'].sudo().search([('code', '=', 'COMJNLTP')], limit=1)

        move_line_array = []
        total_debit = 0
        for customer in customers:
            used_context = {'partner_id': customer.id, 'journal_ids': journal_ids.ids or False, 'state': 'all', 'date_from': start_date, 'date_to': end_date, 'display_account': 'all', 'operating_unit_ids': False, 'strict_range': True if self.start_date else False, 'lang': self.env.context.get('lang') or 'en_US'}
            accounts_result = self._get_account_move_entry(customer.property_account_receivable_id, True, 'all', used_context)

            for account in accounts_result:
                percentage_domain = [
                    ('parent_id', '=', percentage_config.id),
                    ('from_range', '<=', float(account['credit'])),
                    ('to_range', '>=', float(account['credit'])),
                ]
                commission_percentage_config = self.env['commission.prcntg.config.line'].search(percentage_domain, limit=1)
                refund_percentage_config = self.env['refund.prcntg.config.line'].search(percentage_domain, limit=1)

                if commission_percentage_config:
                    commission_amount = (commission_percentage_config.rate * account['credit']) / 100
                    label = "Commission: (%s * %s) / 100" % (commission_percentage_config.rate, account['credit'])
                    credit_move_line_vals = {
                        'name': label,
                        'date': datetime.now().date(),
                        'journal_id': journal_id.id,
                        'account_id': customer.property_account_receivable_id.id,
                        'operating_unit_id': False,
                        'department_id': False,
                        'cost_center_id': False,
                        'debit': 0,
                        'credit': commission_amount,
                        'company_id': percentage_config.company_id.id,
                    }

                    move_line_array.append((0, 0, credit_move_line_vals))
                    total_debit = total_debit + commission_amount

                if refund_percentage_config:
                    refund_amount = (refund_percentage_config.rate * account['credit']) / 100
                    label = "Refund: (%s * %s) / 100" % (refund_percentage_config.rate, account['credit'])
                    credit_move_line_vals = {
                        'name': label,
                        'date': datetime.now().date(),
                        'journal_id': journal_id.id,
                        'account_id': customer.property_account_receivable_id.id,
                        'operating_unit_id': False,
                        'department_id': False,
                        'cost_center_id': False,
                        'debit': 0,
                        'credit': refund_amount,
                        'company_id': percentage_config.company_id.id,
                    }

                    move_line_array.append((0, 0, credit_move_line_vals))
                    total_debit = total_debit + refund_amount

        config_ap_id = self.env['ir.values'].sudo().get_default('sale.config.settings', 'commission_refund_top_up_account')
        acc_id = int(config_ap_id) if config_ap_id else False

        if not acc_id:
            raise Exception("Account Id Not found.")

        debit_move_line = {
            'name': "Slab Commission/Refund",
            'date': datetime.now().date(),
            'journal_id': journal_id.id,
            'account_id': acc_id,
            'operating_unit_id': False,
            'department_id': False,
            'cost_center_id': False,
            'debit': total_debit,
            'credit': 0,
            'company_id': percentage_config.company_id.id,
        }
        move_line_array.append((0, 0, debit_move_line))

        name_seq = self.env['ir.sequence'].next_by_code('commission.refund.account.move.slab.seq')
        vals = {
            'name': name_seq,
            'journal_id': journal_id.id,
            'operating_unit_id': False,
            'date': datetime.now().date(),
            'company_id': percentage_config.company_id.id,
            'partner_id': False,
            'state': 'draft',
            'line_ids': move_line_array,
        }

        _move = self.env['account.move'].sudo().create(vals)
        # if _move:
        #     _move.post()

        percentage_config.cron_executed = True

    @api.model
    def pull_automation_yearly(self):
        print('pull_automation_yearly')


class CommissionPercentageConfigLine(models.Model):
    _name = 'commission.prcntg.config.line'

    parent_id = fields.Many2one('commission.refund.prcntg.config')
    from_range = fields.Float(string='From Range')
    to_range = fields.Float(string='To Range')
    rate = fields.Float(string='Rate(%)', size=3)

    @api.constrains('rate')
    def _rate_constrains(self):
        if self.rate > 100:
            raise ValidationError(_("Rate must be between 0 to 100"))


class RefundPercentageConfigLine(models.Model):
    _name = 'refund.prcntg.config.line'

    parent_id = fields.Many2one('commission.refund.prcntg.config')
    from_range = fields.Float(string='From Range')
    to_range = fields.Float(string='To Range')
    rate = fields.Float(string='Rate(%)', size=3)

    @api.constrains('rate')
    def _rate_constrains(self):
        if self.rate > 100:
            raise ValidationError(_("Rate must be between 0 to 100"))
