from odoo import models, api, _, fields
from odoo.tools.misc import formatLang


class report_account_advance_aged_payable(models.AbstractModel):
    _name = "account.advance.aged.payable"
    _description = "Aged Payable"
    _inherit = "account.aged.partner"

    @api.model
    def get_lines(self, context_id, line_id=None):
        if type(context_id) == int:
            context_id = self.env['account.context.advance.aged.payable'].search([['id', '=', context_id]])
        new_context = dict(self.env.context)
        new_context.update({
            'date_to': context_id.date_to,
            'aged_balance': True,
            'context_id': context_id,
            'company_ids': context_id.company_ids.ids,
            'account_type': 'payable',
            'advance_aged_payable': True,
        })
        return self.with_context(new_context)._lines(context_id, line_id)

    @api.model
    def get_title(self):
        return _("Advance Aged Payable")

    @api.model
    def get_name(self):
        return 'advance_aged_payable'

    @api.model
    def get_report_type(self):
        return self.env.ref('account_reports.account_report_type_nothing')

    def get_template(self):
        return 'account_reports.report_financial'


class account_context_advance_aged_payable(models.TransientModel):
    _name = "account.context.advance.aged.payable"
    _description = "A particular context for the aged payable"
    _inherit = "account.report.context.common"

    fold_field = 'unfolded_partners'
    unfolded_partners = fields.Many2many('res.partner', 'advance_aged_payable_context_to_partner', string='Unfolded lines')

    def get_report_obj(self):
        return self.env['account.advance.aged.payable']

    def get_columns_names(self):
        return [_(u"Not\N{NO-BREAK SPACE}due\N{NO-BREAK SPACE}on %s") % self.date_to,
                u"0\N{NO-BREAK SPACE}-\N{NO-BREAK SPACE}30",
                u"30\N{NO-BREAK SPACE}-\N{NO-BREAK SPACE}60",
                u"60\N{NO-BREAK SPACE}-\N{NO-BREAK SPACE}90",
                u"90\N{NO-BREAK SPACE}-\N{NO-BREAK SPACE}120",
                _(u"Older"),
                _(u"Total")]

    @api.multi
    def get_columns_types(self):
        return ["number", "number", "number", "number", "number", "number", "number"]