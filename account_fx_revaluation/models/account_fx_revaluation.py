import logging
from itertools import groupby

from odoo import api, fields, models, _
from odoo import tools
from odoo.exceptions import UserError, ValidationError, Warning

_logger = logging.getLogger(__name__)


class AccountFxRevaluation(models.Model):
    _name = 'account.fx.revaluation'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'FX Revaluation'
    _order = 'id desc'

    name = fields.Char(string='Name', copy=False, track_visibility='onchange')
    date = fields.Date(string='Date ', required=True, default=fields.Date.today(), readonly=True,
                       states={'draft': [('readonly', False)]}, track_visibility='onchange')
    total_revaluation_amount = fields.Float(string='Profit/Loss Amount', readonly=True,
                                            states={'draft': [('readonly', False)]}, track_visibility='onchange')
    description = fields.Text(string='Narration', required='True', readonly=True,
                              states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('revaluate', 'Revaluated'), ('confirmed', 'Confirmed')],
                             default='draft', string="Status", copy=False, track_visibility='onchange')

    # relational field
    account_fx_revaluation_line_ids = fields.One2many('account.fx.revaluation.line', 'account_fx_revaluation_id',
                                                      copy=False)
    move_id = fields.Many2one('account.move', string='Journal Entry', readonly=True, copy=False)

    total_lcy_amount = fields.Float(string='LCY Amount', compute='_compute_total_amount')
    total_fcy_amount = fields.Float(string='FCY Amount', compute='_compute_total_amount', digits=(12, 3))

    @api.constrains('date')
    def _constrains_date(self):
        if self.date:
            account_fx_revaluation_id = self.search([('date', '=', self.date)])
            if len(account_fx_revaluation_id.ids) > 1:
                raise ValidationError(_('You are not allowed to do multiple time revaluation in a single day.'))

    @api.depends('account_fx_revaluation_line_ids')
    def _compute_total_amount(self):
        for record in self:
            record.total_lcy_amount = sum([rec.total_lcy_amount for rec in record.account_fx_revaluation_line_ids])
            record.total_fcy_amount = sum([rec.total_fcy_amount for rec in record.account_fx_revaluation_line_ids])

    @api.one
    def revaluation_process(self, sequence):
        self.ensure_one()

        account_ids = self.env['account.account'].search([('revaluation', '=', True)])
        if len(account_ids.ids) <= 0:
            raise Warning(_("There is no such GL to revaluate. \nPlease configure the GL first."))

        fy_start_date = self.env['date.range'].search(
            [('type_id.fiscal_year', '=', True), ('date_start', '<=', self.date),
             ('date_end', '>=', self.date)]).date_start
        if not fy_start_date:
            raise ValidationError(
                _("There is no financial year has been created. \nPlease  create financial year, then process again."))

        currency_ids = self.env['res.currency'].search(
            [('id', '!=', self.env.user.company_id.currency_id.id), ('active', '=', True)])
        currency_rates = self.get_currency_current_rate(currency_ids, self.date)

        branch_ids = self._get_branches()

        account_fx_revaluation_line_details_ids = self.get_account_fx_revaluation_line_details_ids(fy_start_date,
                                                                                                   account_ids,
                                                                                                   currency_ids,
                                                                                                   currency_rates,
                                                                                                   branch_ids)
        account_fx_revaluation_line_ids = self.get_account_fx_revaluation_line_ids(
            account_fx_revaluation_line_details_ids)
        total_revaluation_amount = sum(
            val['revaluation_amount'] for key, val in account_fx_revaluation_line_ids.iteritems())

        self.write({
            'name': sequence,
            'total_revaluation_amount': total_revaluation_amount,
            'state': 'revaluate',
            'account_fx_revaluation_line_ids': [(0, 0, val) for key, val in account_fx_revaluation_line_ids.iteritems()]
        })

        # For Acocunt FX Revaluation Line Details Pivot View
        # self.env['account.fx.revaluation.details.report'].with_context(
        #     {'account_fx_revaluation_id': self.id,
        #      'company_id': self.env.user.company_id.id}).init()

    def _get_branches(self):
        branch_ids = self.env['operating.unit'].search(['|', ('obu', '=', False), ('obu', '=', None)]).ids
        return branch_ids

    @api.multi
    def action_revaluate(self):
        if self.state == 'draft':
            for fxr in self:
                sequence = self.env['ir.sequence'].next_by_code('account.fx.revaluation') or ''
                fxr.revaluation_process(sequence)

    @api.multi
    def action_re_revaluate(self):
        if self.state == 'revaluate':
            for fxr in self:
                # delete existing line records
                fxr.account_fx_revaluation_line_ids.unlink()
                fxr.revaluation_process(fxr.name)

    @api.model
    def action_revaluation_details(self):
        self.ensure_one()
        self.env['account.fx.revaluation.details.report'].with_context(
            {'account_fx_revaluation_id': self.id,
             'company_id': self.env.user.company_id.id}).init()

        view_ref = self.env['ir.model.data'].get_object_reference('account_fx_revaluation',
                                                                  'view_account_fx_revaluation_details_report_pivot')
        view_id = view_ref and view_ref[1] or False,

        return {
            "type": "ir.actions.act_window",
            'name': 'FX Revaluation Details',
            "res_model": "account.fx.revaluation.details.report",
            "view_mode": "pivot",
            "view_type": "pivot",
            "res_id": self.id,
            "view_id": view_id,
            "context": {'search_default_current': 1, 'group_by': [], 'group_by_no_leaf': 1}
        }

    @api.multi
    def action_confirm(self):
        if self.state != 'revaluate':
            raise ValidationError(_("[STATE] Operation has done already."))

        if not self.env.user.company_id.fx_revaluation_journal_id.id:
            raise ValidationError(_("[Validation Error] Configure the FX Revaluation Journal!!"))

        if not self.env.user.company_id.fx_revaluation_account_id.id:
            raise ValidationError(_("[Validation Error] Configure the FX Revaluation Account!!"))

        fxr_check = self.env['account.move'].search([('ref', '=', self.name)])
        if fxr_check:
            raise ValidationError(_("[Validation Error] Fx Revaluation already processing."))
        journal = self.env.user.company_id.fx_revaluation_journal_id.id
        company = self.env.user.company_id
        amount = 0.0

        move = self.env['account.move'].create({
            'journal_id': journal,
            'date': self.date,
            'state': 'draft',
            'is_cbs': True,
            'name': self.name,
            'ref': self.name,
            'company_id': company.id,
        })

        move_lines = []
        journal_entry = ''
        date = self.date or fields.date.today()

        for line in self.account_fx_revaluation_line_ids:
            for detail in line.account_fx_revaluation_line_details_ids:
                # branch details wise debit or credit line
                debit, credit = 0.0, 0.0
                if detail.profit_loss_amount == 0:
                    continue
                elif detail.profit_loss_amount < 0:
                    credit = abs(round(detail.profit_loss_amount, 2))
                else:
                    debit = abs(round(detail.profit_loss_amount, 2))

                line1 = {
                    'name': self.description or 'FX Revaluation',
                    'ref': self.name,
                    'date': date,
                    'account_id': detail.account_id.id,
                    'currency_id': detail.currency_id.id,
                    'operating_unit_id': detail.operating_unit_id.id,
                    'amount_currency': 0.0,
                    'debit': debit,
                    'credit': credit,
                    'company_id': company.id,
                    'date_maturity': date,
                    'sub_operating_unit_id': 'NULL',
                    'amount_currency': 0.0,
                    'journal_id': journal,
                    'move_id': move.id,
                    'is_bgl': 'not_check'
                }

                journal_entry += self.format_journal(line1)

            # branch wise debit or credit line
            debit2, credit2 = 0.0, 0.0
            if line.revaluation_amount == 0:
                continue
            elif line.revaluation_amount < 0:
                debit2 = abs(round(line.revaluation_amount, 2))
            else:
                credit2 = abs(round(line.revaluation_amount, 2))

            line2 = {
                'name': self.description or 'FX Revaluation',
                'ref': self.name,
                'date': date,
                'account_id': self.env.user.company_id.fx_revaluation_account_id.id,
                'currency_id': self.env.user.company_id.currency_id.id,
                'operating_unit_id': line.operating_unit_id.id,
                'amount_currency': 0.0,
                'debit': debit2,
                'credit': credit2,
                'company_id': company.id,
                'date_maturity': date,
                'sub_operating_unit_id': 'NULL',
                'journal_id': journal,
                'move_id': move.id,
                'is_bgl': 'not_check'
            }
            amount += debit2 if debit2 > 0 else credit2
            journal_entry += self.format_journal(line2)

        if not journal_entry:
            raise ValidationError(_("Credit/Debit should not be empty."))

        query = """INSERT INTO account_move_line 
                                (move_id, date,date_maturity, operating_unit_id, account_id, name,ref, currency_id, journal_id,
                                credit,debit,amount_currency,company_id,is_bgl,sub_operating_unit_id)  
                                VALUES %s""" % journal_entry[:-1]
        self.env.cr.execute(query)
        if move:
            move.write({'amount': amount})
            move.sudo().post()
            self.write({'state': 'confirmed',
                        'move_id': move.id
                        })

    @api.multi
    def get_currency_current_rate(self, currency_ids, date):
        date_str = date + ' 23:59:59'
        company_id = self._context.get('company_id') or self.env['res.users']._get_company().id
        query = """SELECT c.id, (SELECT r.reverse_rate FROM res_currency_rate r
                                  WHERE r.currency_id = c.id AND r.name <= %s
                                    AND (r.company_id IS NULL OR r.company_id = %s)
                               ORDER BY r.company_id, r.name DESC
                                  LIMIT 1) AS rate
                   FROM res_currency c
                   WHERE c.id IN %s"""
        self._cr.execute(query, (date_str, company_id, tuple(currency_ids.ids)))
        currency_rates = dict(self._cr.fetchall())

        return currency_rates

    @api.multi
    def get_account_fx_revaluation_line_ids(self, line_details):
        lines = {}
        for key, val in groupby(line_details, key=lambda x: x[2]['operating_unit_id']):
            account_fx_revaluation_line_details_ids = list(val)
            revaluation_amount = sum(line[2]['profit_loss_amount'] for line in account_fx_revaluation_line_details_ids)

            if key in lines:
                lines[key]['account_fx_revaluation_line_details_ids'].append(account_fx_revaluation_line_details_ids)
            else:
                lines[key] = {
                    'operating_unit_id': key,
                    'revaluation_amount': revaluation_amount,
                    'account_fx_revaluation_line_details_ids': account_fx_revaluation_line_details_ids
                }
        return lines

    @api.multi
    def get_account_fx_revaluation_line_details_ids(self, fy_start_date, account_ids, currency_ids, currency_rates,
                                                    branch_ids):
        # query to fetch data
        sql_str = """SELECT
                        aml.operating_unit_id,
                        aml.account_id,
                        aml.currency_id,
                        SUM(aml.amount_currency) AS fc_amount,
                        (SUM(aml.credit) - SUM(aml.debit)) AS lcy_amount
                    FROM
                        account_move_line aml
                        LEFT JOIN operating_unit ou ON ou.id=aml.operating_unit_id
                        LEFT JOIN account_account aa ON aa.id=aml.account_id
                        LEFT JOIN res_currency rc ON rc.id=aml.currency_id
                    WHERE
                        aml.date BETWEEN %s AND %s
                        AND aa.revaluation = True
                        AND aml.currency_id IN %s
                        AND ou.id IN %s
                    GROUP BY
                        aml.operating_unit_id,
                        aml.account_id,
                        aml.currency_id
                    ORDER BY aml.operating_unit_id ASC
        """

        self._cr.execute(sql_str, (fy_start_date, self.date, tuple(currency_ids.ids), tuple(branch_ids)))
        result = self._cr.fetchall()

        details = []
        for val in result:
            currency_id = int(val[2])
            fc_amount = float(val[3])
            lcy_amount = round(float(val[4]), 2)
            holding_rate = 0 if fc_amount == 0 else (lcy_amount / fc_amount)
            revaluation_rate = currency_rates.get(currency_id) or 1.0
            mtm_amount = round((fc_amount * revaluation_rate), 2)
            profit_loss_amount = round((lcy_amount - mtm_amount), 2)

            details_vals = {
                'operating_unit_id': int(val[0]),
                'account_id': int(val[1]),
                'currency_id': currency_id,
                'fc_amount': fc_amount,
                'lcy_amount': lcy_amount,
                'holding_rate': holding_rate,
                'revaluation_rate': revaluation_rate,
                'mtm_amount': mtm_amount,
                'profit_loss_amount': profit_loss_amount
            }

            details.append((0, 0, details_vals))

        return details

    @api.multi
    def unlink(self):
        for revaluation in self:
            if revaluation.state not in ('draft', 'revaluate'):
                raise UserError(
                    _('You cannot delete a FX Revaluation which is not draft.'))
        return super(AccountFxRevaluation, self).unlink()

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ('draft', 'revaluate', 'confirmed'))]

    @staticmethod
    def format_journal(line):
        return "({0},'{1}','{2}',{3},{4},'{5}','{6}',{7},{8},{9},{10},{11},{12},'{13}',{14}),".format(
            line['move_id'],
            line['date'],
            line['date_maturity'],
            line['operating_unit_id'],
            line['account_id'],
            line['name'],
            line['name'],
            line['currency_id'],
            line['journal_id'],
            line['credit'],
            line['debit'],
            line['amount_currency'],
            line['company_id'],
            line['is_bgl'],
            line['sub_operating_unit_id'],
        )


class AccountFxRevaluationLine(models.Model):
    _name = 'account.fx.revaluation.line'
    _order = 'operating_unit_id ASC'

    account_fx_revaluation_id = fields.Many2one('account.fx.revaluation', ondelete='cascade')
    operating_unit_id = fields.Many2one('operating.unit', string='Branch', required=True)
    revaluation_amount = fields.Float(string='Profit/Loss Amount', reuired=True)
    total_lcy_amount = fields.Float(string='LCY Amount', compute='_compute_total_amount')
    total_fcy_amount = fields.Float(string='FCY Amount', compute='_compute_total_amount', digits=(12, 3))

    # relational field
    account_fx_revaluation_line_details_ids = fields.One2many('account.fx.revaluation.line.details',
                                                              'account_fx_revaluation_line_id', copy=False)

    @api.depends('account_fx_revaluation_line_details_ids')
    def _compute_total_amount(self):
        for record in self:
            record.total_lcy_amount = sum([rec.lcy_amount for rec in record.account_fx_revaluation_line_details_ids])
            record.total_fcy_amount = sum([rec.fc_amount for rec in record.account_fx_revaluation_line_details_ids])


class AccountFxRevaluationLineDetails(models.Model):
    _name = 'account.fx.revaluation.line.details'
    _order = 'currency_id DESC'

    account_fx_revaluation_line_id = fields.Many2one('account.fx.revaluation.line', ondelete='cascade')
    account_id = fields.Many2one('account.account', string="GL Account", required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True)
    operating_unit_id = fields.Many2one('operating.unit', string='Branch', required=True)
    fc_amount = fields.Float(string='FCY Amount', reuired=True, digits=(12, 3))
    lcy_amount = fields.Float(string='LCY Amount', reuired=True)
    holding_rate = fields.Float(string='Holding Rate')
    revaluation_rate = fields.Float(string='Revaluation Rate', digits=(12, 8))
    mtm_amount = fields.Float(string='MTM')
    profit_loss_amount = fields.Float(string='Profit/Loss Amount')


class AccountFxRevaluationLineDetailsReport(models.Model):
    _name = "account.fx.revaluation.details.report"
    _auto = False
    _rec_name = 'date'

    date = fields.Date(readonly=True)
    state = fields.Selection([('draft', "Draft"), ('revaluate', "Revaluated")], string="Status", readonly=True)
    account_id = fields.Many2one('account.account', string="GL Account", readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True)
    operating_unit_id = fields.Many2one('operating.unit', string='Branch', readonly=True)
    fc_amount = fields.Float(string='FCY Amount', readonly=True, digits=(12, 3))
    lcy_amount = fields.Float(string='LCY Amount', readonly=True)
    holding_rate = fields.Float(string='Holding Rate', readonly=True, group_operator="avg")
    revaluation_rate = fields.Float(string='Revaluation Rate', readonly=True, group_operator="avg", digits=(12, 8))
    mtm_amount = fields.Float(string='MTM', readonly=True)
    profit_loss_amount = fields.Float(string='Profit/Loss Amount', readonly=True)

    _order = 'date desc'

    _depends = {
        'account.fx.revaluation': ['date', 'state'],
        'account.fx.revaluation.line': ['account_fx_revaluation_id', 'operating_unit_id'],
        'account.fx.revaluation.line.details': [
            'account_fx_revaluation_line_id', 'account_id', 'currency_id', 'operating_unit_id',
            'fc_amount', 'lcy_amount', 'holding_rate', 'revaluation_rate', 'mtm_amount', 'profit_loss_amount'
        ],
    }

    def _select(self):
        select_str = """
                SELECT sub.id, sub.date, sub.account_id, sub.currency_id, sub.operating_unit_id,
                    sub.fc_amount, sub.lcy_amount, sub.holding_rate, sub.revaluation_rate, sub.mtm_amount,
                    sub.profit_loss_amount, sub.state
            """
        return select_str

    def _sub_select(self):
        select_str = """
                    SELECT rld.id AS id, rld.account_id, rld.currency_id, rld.operating_unit_id, rld.fc_amount,
                        rld.lcy_amount, rld.holding_rate, rld.revaluation_rate, rld.mtm_amount, rld.profit_loss_amount,
                        fxr.date AS date, fxr.state    
            """
        return select_str

    def _from(self):
        from_str = """
                    FROM account_fx_revaluation_line_details rld
                    JOIN account_fx_revaluation_line rl ON rl.id = rld.account_fx_revaluation_line_id
                    JOIN account_fx_revaluation fxr ON fxr.id = rl.account_fx_revaluation_id
            """
        return from_str

    def _where(self, account_fx_revaluation_id):
        where_str = """
                    WHERE account_fx_revaluation_id = %s
        """ % (account_fx_revaluation_id)

        return where_str

    def _group_by(self):
        group_by_str = """
                    GROUP BY rld.id, rld.account_id, rld.currency_id, rld.operating_unit_id, rld.fc_amount, 
                    rld.lcy_amount, rld.holding_rate, rld.revaluation_rate, rld.mtm_amount, rld.profit_loss_amount,
                    fxr.date, fxr.state
            """
        return group_by_str

    @api.model_cr
    def init(self):
        if self.env.context.get('account_fx_revaluation_id', False):
            account_fx_revaluation_id = self.env.context.get('account_fx_revaluation_id')
            tools.drop_view_if_exists(self.env.cr, self._table)
            self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
                                %s
                                FROM (
                                    %s %s %s %s
                                ) AS sub
                            )""" % (
                self._table, self._select(), self._sub_select(), self._from(),
                self._where(account_fx_revaluation_id), self._group_by()))
