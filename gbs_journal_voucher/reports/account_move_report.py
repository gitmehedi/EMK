from odoo import api, models, fields


class AccountMoveReport(models.AbstractModel):
    _name = 'report.gbs_journal_voucher.account_move_report'

    @api.multi
    def render_html(self, docids, data=None):
        report_data = self.env['account.move'].browse(docids[0])
        docargs = {
            'docs': report_data,
        }

        return self.env['report'].render('gbs_journal_voucher.account_move_report', docargs)
