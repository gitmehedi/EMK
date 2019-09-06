# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountBalanceReport(models.TransientModel):
    _inherit = 'account.balance.report'

    @api.multi
    def button_export_xlsx(self):
        self.ensure_one()
        return self.env['report'].get_action(self, report_name='account_reports_xls.payroll_xls')
