# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountBalanceReport(models.TransientModel):
    _inherit = 'account.balance.report'

    operating_unit_ids = fields.Many2many(string='Branch')

    @api.multi
    def button_export_xlsx(self, data):
        self.ensure_one()
        return self.env['report'].get_action(self, report_name='account_reports_xls.payroll_xls')
