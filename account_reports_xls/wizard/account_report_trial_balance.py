# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountBalanceReport(models.TransientModel):
    _inherit = 'account.balance.report'

    @api.multi
    def button_export_xlsx(self):
        self.ensure_one()
        return self._export(xlsx_report=True)

    def _export(self, xlsx_report=False):
        """Default export is PDF."""
        model = self.env['report_trial_balance_qweb']
        report = model.create(self._prepare_report_trial_balance())
        return report.print_report(xlsx_report)

    def _prepare_report_trial_balance(self):
        self.ensure_one()
        return {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'only_posted_moves': self.target_move == 'posted',
            # 'hide_account_balance_at_0': self.hide_account_balance_at_0,
            'hide_account_balance_at_0': True,
            'company_id': self.company_id.id,
            # 'filter_account_ids': [(6, 0, self.account_ids.ids)],
            'filter_account_ids': [],
            # 'filter_partner_ids': [(6, 0, self.partner_ids.ids)],
            # 'fy_start_date': self.fy_start_date,
            # 'show_partner_details': self.show_partner_details,
        }
