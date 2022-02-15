from odoo import models, fields, api, _


class AccountReportContextCommon(models.TransientModel):
    _inherit = 'account.report.context.common'

    def _report_name_to_report_model(self):
        res = super(AccountReportContextCommon, self)._report_name_to_report_model()
        res.update({'advance_aged_payable': 'account.advance.aged.payable'})
        return res

    def _report_model_to_report_context(self):
        res = super(AccountReportContextCommon, self)._report_model_to_report_context()
        res.update({'account.advance.aged.payable': 'account.context.advance.aged.payable'})
        return res
