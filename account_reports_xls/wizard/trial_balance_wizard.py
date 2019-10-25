# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountBalanceReport(models.TransientModel):
    _inherit = 'account.balance.report'

    operating_unit_ids = fields.Many2many(string='Branch (Include)')
    ex_operating_unit_ids = fields.Many2many('operating.unit', 'account_balance_report_ex_operating_unit_rel',
                                             'account_id', 'operating_unit_id', string='Branch (Exclude)',
                                             required=False, default=[])

    def _build_contexts(self, data):
        result = super(AccountBalanceReport, self)._build_contexts(data)
        data2 = {}
        data2['form'] = self.read(['ex_operating_unit_ids'])[0]
        result['ex_operating_unit_ids'] = 'ex_operating_unit_ids' in data2['form'] and \
                                          data2['form']['ex_operating_unit_ids'] or False
        return result

    def _print_report(self, data):
        ex_operating_units = ', '.join([ou.name for ou in self.ex_operating_unit_ids])
        data['form'].update({'ex_operating_units': ex_operating_units})
        return super(AccountBalanceReport, self)._print_report(data)

    @api.multi
    def button_export_xlsx(self, data):
        self.ensure_one()
        return self.env['report'].get_action(self, report_name='account_reports_xls.payroll_xls')
