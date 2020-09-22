# -*- coding: utf-8 -*-
from datetime import datetime as dt

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class AccountBalanceReport(models.TransientModel):
    _inherit = 'account.balance.report'

    operating_unit_ids = fields.Many2many(string='Branch (Include)')
    ex_operating_unit_ids = fields.Many2many('operating.unit', 'account_balance_report_ex_operating_unit_rel',
                                             'account_id', 'operating_unit_id', string='Branch (Exclude)',
                                             required=False, default=[])
    include_profit_loss = fields.Boolean(string="Include Profit/Loss", default=False)
    is_tb_exc = fields.Boolean(string="Trial Balance (Exclude)", default=False)

    @api.constrains('date_from', 'date_to')
    def check_date(self):
        if self.date_from:
            if self.date_to:
                start = dt.strptime(self.date_from, "%Y-%m-%d")
                end = dt.strptime(self.date_to, "%Y-%m-%d")
                start_year = self.date_from[:4]
                end_year = self.date_to[:4]
                msg = ''
                if start > end:
                    msg += "Start Date [{0}] shouldn't be greater than End Date [{1}]\n".format(self.date_from,
                                                                                                self.date_to)
                if start_year != end_year:
                    msg += "Start Date [{0}] and End Date [{1}] should be in same year.".format(self.date_from,
                                                                                                self.date_to)

                if msg:
                    raise ValidationError(_(msg))

    def _build_contexts(self, data):
        result = super(AccountBalanceReport, self)._build_contexts(data)
        data2 = {}
        data2['form'] = self.read(['ex_operating_unit_ids'])[0]
        result['ex_operating_unit_ids'] = 'ex_operating_unit_ids' in data2['form'] and \
                                          data2['form']['ex_operating_unit_ids'] or False
        result['include_profit_loss'] = self.include_profit_loss
        result['is_tb_exc'] = self.is_tb_exc
        return result

    def _print_report(self, data):
        ex_operating_units = ', '.join([ou.name for ou in self.ex_operating_unit_ids])
        data['form'].update({'ex_operating_units': ex_operating_units,'include_profit_loss':self.include_profit_loss})
        return super(AccountBalanceReport, self)._print_report(data)

    @api.multi
    def button_export_xlsx(self, data):
        self.ensure_one()
        return self.env['report'].get_action(self, report_name='account_reports_xls.payroll_xls')
